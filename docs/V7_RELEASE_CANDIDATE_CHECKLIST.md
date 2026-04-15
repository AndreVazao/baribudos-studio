# V7 Release Candidate Checklist

## Objective

Close V7 as a usable release candidate fast, with the smallest possible path to:
- Windows EXE
- Android APK
- real Studio to Website publication
- first sellable ebook or audiobook surface

## Build gates

### Desktop
- [ ] `Manual Build Windows EXE` green
- [ ] Windows bundle artifact available
- [ ] desktop bundle can be downloaded from GitHub Actions

### Mobile
- [ ] `android-apk.yml` green
- [ ] APK artifact available
- [ ] APK can be downloaded from GitHub Actions

## Core operation gates

### Studio
- [ ] Studio CI green on V7
- [ ] Distribution Hub smoke green
- [ ] Studio V7 publish ops available
- [ ] Studio V7 website visibility available

### Website
- [ ] Website CI green on V7
- [ ] Studio ingest route available
- [ ] project status route available
- [ ] catalog status route available
- [ ] selling status route available

## First real content flow
- [ ] choose one real project
- [ ] validate production readiness
- [ ] sync readiness
- [ ] freeze preview
- [ ] freeze package
- [ ] publish to website
- [ ] inspect website project status
- [ ] inspect website catalog status
- [ ] inspect website selling status
- [ ] confirm product appears on public surfaces

## Public selling surfaces to verify
- [ ] /
- [ ] /comprar
- [ ] /primeira-compra
- [ ] /lancamentos
- [ ] /ebooks
- [ ] /audiobooks
- [ ] /loja
- [ ] /novidades
- [ ] /em-breve

## Definition of ready to merge V7
- [ ] Studio branch green
- [ ] Website branch green
- [ ] EXE build green
- [ ] APK build green
- [ ] first real project published and visible
- [ ] no blocker left on core production, freeze, publish or sell flow

## Immediate next action after merge
- [ ] use new PC to download Windows EXE artifact path
- [ ] use mobile to download APK artifact path
- [ ] run the first real production cycle
