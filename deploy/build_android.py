import subprocess

def build():
    print("📱 Building Android APK...")

    subprocess.run(["buildozer", "android", "debug"])

    print("✅ APK build complete")

if __name__ == "__main__":
    build()
