#!/bin/bash
set -e

SERVICE_NAME="mancer-watercooler.service"
SERVICE_TEMPLATE="systemd/mancer-watercooler.service"
SERVICE_DST="/etc/systemd/system/$SERVICE_NAME"

# Descobre o usuário real (mesmo usando sudo)
REAL_USER=${SUDO_USER:-$(whoami)}
USER_HOME=$(eval echo "~$REAL_USER")
INSTALL_PATH="$USER_HOME/displaywatercoolermanceronubuntu"

echo "👤 Usuário detectado: $REAL_USER"
echo "📂 Caminho do projeto: $INSTALL_PATH"

# Garante que está sendo executado do diretório correto
if [ ! -f "$INSTALL_PATH/watercooler.py" ]; then
  echo "❌ Erro: watercooler.py não encontrado em $INSTALL_PATH"
  exit 1
fi

echo "📦 Instalando dependências..."
sudo apt update
sudo apt install -y python3 python3-pip python3-psutil python3-usb

echo "⚙️ Gerando serviço systemd..."
sed "s|__INSTALL_PATH__|$INSTALL_PATH|g" "$SERVICE_TEMPLATE" | sudo tee "$SERVICE_DST" > /dev/null

echo "🔄 Recarregando systemd..."
sudo systemctl daemon-reload

echo "🚀 Ativando serviço..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Instalação concluída com sucesso!"
echo "ℹ️ Status do serviço:"
sudo systemctl status "$SERVICE_NAME" --no-pager
