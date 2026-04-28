# INFRA_GCP_RUTAS_REPOS — SMARTPYME FACTORY

## GCP
Project: smartseller-490511

## VM
Nombre: smartpyme-factory (validar)
Path base:
/opt/smartpyme-factory

## REPOS

SmartPyme:
https://github.com/smartdash-almasana/SmartPyme
/opt/smartpyme-factory/repos/SmartPyme

Hermes:
/opt/smartpyme-factory/repos/hermes-agent

## RUNNER
/opt/smartpyme-factory/run_sfma_cycle.sh

## SERVICE
smartpyme-sfma.service

## MANUAL
/opt/smartpyme-factory/repos/SmartPyme/docs/factory/GPT_HERMES_EXECUTION_MANUAL.md

## COMANDOS

ssh:
gcloud compute ssh smartpyme-factory --zone <ZONA>

update:
cd /opt/smartpyme-factory/repos/SmartPyme && git pull --ff-only origin main

logs:
sudo journalctl -u smartpyme-sfma.service --no-pager

diagnostic:
find /opt/smartpyme-factory -maxdepth 3 -type d | sort

## ESTADO

- repo OK
- hermes sin token telegram
- runner presente

## REGLA

NO usar Cloud Shell para systemd
