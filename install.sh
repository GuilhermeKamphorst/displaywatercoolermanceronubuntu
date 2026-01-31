#!/bin/bash
set -e

SERVICE_NAME="mancer-watercooler.service"
SERVICE_SRC="systemd/$SERVICE_NAME"
SERVICE_DST="/etc/systemd/system/$SERVICE_NAME"

echo "📦 Instalando dependências do sistema..."
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  python3-psutil \
  python3-usb

echo "🔗 Instalando serviço systemd..."
sudo ln -sf "$(pwd)/$SERVICE_SRC" "$SERVICE_DST"

echo "🔄 Recarregando systemd..."
sudo systemctl daemon-reload

echo "🚀 Habilitando e iniciando serviço..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Serviço instalado e iniciado com sucesso"
