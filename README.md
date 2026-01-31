Mancer Watercooler Display for Linux

Script em Python para controlar e exibir informações no display de watercoolers Mancer no Linux, utilizando acesso USB direto e integração com o systemd.

O projeto instala um serviço que inicia automaticamente junto com o sistema.

Requisitos

Linux (testado no Ubuntu)

Python 3

systemd

Acesso root (necessário para USB e instalação do serviço)

Instalação

Clonar o repositório

Entre na pasta onde deseja instalar o projeto e execute:

```git clone https://github.com/GuilhermeKamphorst/displaywatercoolermanceronubuntu.git```

```cd displaywatercoolermanceronubuntu```

Tornar o instalador executável

```chmod +x install.sh```

Executar o instalador

```sudo ./install.sh```

O serviço será instalado, habilitado e iniciado automaticamente.

Serviço systemd

O serviço instalado se chama:

mancer-watercooler.service

Comandos úteis:

sudo systemctl status mancer-watercooler.service
sudo systemctl restart mancer-watercooler.service
sudo systemctl stop mancer-watercooler.service

Observações

O serviço roda como root para permitir acesso USB.

O projeto ainda está em desenvolvimento e pode sofrer alterações.

Licença

Uso livre para fins educacionais e experimentais.
