use keyring::Entry;

const KEYRING_SERVICE: &str = "com.baribudos.studio";
const KEYRING_USER: &str = "studio-session-token";

fn session_entry() -> Result<Entry, String> {
    Entry::new(KEYRING_SERVICE, KEYRING_USER)
        .map_err(|_| "Não foi possível abrir o cofre de credenciais do sistema.".to_string())
}

#[tauri::command]
fn secure_session_get() -> Result<Option<String>, String> {
    let entry = session_entry()?;
    match entry.get_password() {
        Ok(token) => Ok(Some(token)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(_) => Err("Não foi possível ler a sessão do cofre do sistema.".to_string()),
    }
}

#[tauri::command]
fn secure_session_set(token: String) -> Result<(), String> {
    if token.trim().is_empty() || token.len() > 4096 {
        return Err("Token de sessão inválido.".to_string());
    }
    session_entry()?
        .set_password(token.trim())
        .map_err(|_| "Não foi possível guardar a sessão no cofre do sistema.".to_string())
}

#[tauri::command]
fn secure_session_clear() -> Result<(), String> {
    let entry = session_entry()?;
    match entry.delete_credential() {
        Ok(()) | Err(keyring::Error::NoEntry) => Ok(()),
        Err(_) => Err("Não foi possível remover a sessão do cofre do sistema.".to_string()),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            secure_session_get,
            secure_session_set,
            secure_session_clear
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
