#!/usr/bin/env python3
"""
Programa final para Watercooler Mancer
Protocolo descoberto: [temperatura, 0x00, 0x00]
"""

import usb.core
import usb.util
import time
import psutil
import signal
import sys
import os
from datetime import datetime

class MancerWaterCoolerFinal:
    def __init__(self):
        # IDs do dispositivo
        self.VENDOR_ID = 0xaa88
        self.PRODUCT_ID = 0x8666
        self.device = None
        self.connected = False
        self.running = True
        
        # Configurações
        self.update_interval = 1  # Atualiza a cada 1 segundo
        self.max_temp_history = 30  # Histórico de temperaturas
        
        # Histórico para gráfico
        self.temp_history = []
        
        # Cores para terminal
        self.COLORS = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'gray': '\033[90m',
            'reset': '\033[0m'
        }
        
        # Configurar handler para Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Conectar
        self.connect()
    
    def signal_handler(self, sig, frame):
        """Lida com Ctrl+C"""
        print(f"\n{self.COLORS['yellow']}🛑 Desligando...{self.COLORS['reset']}")
        self.running = False
        time.sleep(0.5)
        sys.exit(0)
    
    def print_color(self, text, color='green'):
        """Imprime texto colorido"""
        print(f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}")
    
    def connect(self):
        """Conecta ao watercooler"""
        try:
            self.print_color("🔌 Conectando ao watercooler Mancer...", 'blue')
            
            # Encontra dispositivo
            self.device = usb.core.find(
                idVendor=self.VENDOR_ID, 
                idProduct=self.PRODUCT_ID
            )
            
            if not self.device:
                self.print_color("❌ Dispositivo não encontrado!", 'red')
                self.print_color("   Verifique a conexão USB.", 'yellow')
                return False
            
            # Configura dispositivo
            try:
                if self.device.is_kernel_driver_active(0):
                    self.device.detach_kernel_driver(0)
            except:
                pass
            
            self.device.set_configuration()
            self.connected = True
            
            self.print_color("✅ Conectado com sucesso!", 'green')
            self.print_color("📟 Protocolo: [temperatura, 0x00, 0x00]", 'cyan')
            return True
            
        except Exception as e:
            self.print_color(f"❌ Erro de conexão: {e}", 'red')
            return False
    
    def get_cpu_temperature(self):
        """Obtém temperatura da CPU com múltiplos fallbacks"""
        try:
            temps = psutil.sensors_temperatures()
            
            # Lista de sensores para tentar (em ordem de prioridade)
            sensors_to_try = [
                'coretemp',      # Intel
                'k10temp',       # AMD antigo
                'zenpower',      # AMD Ryzen
                'nvme',          # SSD NVMe
                'amdgpu',        # GPU AMD
                'acpitz',        # Termal zone ACPI
            ]
            
            for sensor in sensors_to_try:
                if sensor in temps and temps[sensor]:
                    # Pega o maior valor dos cores
                    temp_values = []
                    for entry in temps[sensor]:
                        if hasattr(entry, 'current'):
                            temp_values.append(entry.current)
                    
                    if temp_values:
                        return max(temp_values)
            
            # Fallback: procura qualquer temperatura disponível
            all_temps = []
            for sensor_name, sensor_data in temps.items():
                for entry in sensor_data:
                    if hasattr(entry, 'current'):
                        all_temps.append(entry.current)
            
            if all_temps:
                return max(all_temps)
            
            # Se não encontrar nada, retorna valor razoável
            return 40.0
            
        except Exception as e:
            self.print_color(f"⚠️  Erro ao ler sensor: {e}", 'yellow')
            return 40.0
    
    def get_cpu_usage(self):
        """Obtém uso da CPU"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def get_ram_usage(self):
        """Obtém uso de RAM"""
        try:
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def send_to_display(self, temperature):
        """Envia temperatura para o display - PROTOCOLO CORRETO"""
        if not self.connected or not self.device:
            return False
        
        try:
            # PROTOCOLO CORRETO DESCOBERTO: [temperatura, 0x00, 0x00]
            temp_int = int(round(temperature))
            
            # Limita a faixa razoável (0-100°C)
            if temp_int < 0:
                temp_int = 0
            elif temp_int > 100:
                temp_int = 100
            
            # Cria pacote de dados
            data = bytes([temp_int, 0x00, 0x00])
            
            # Envia para o dispositivo
            # Endpoint 0x01 é comum para dispositivos HID simples
            self.device.write(0x01, data)
            return True
            
        except Exception as e:
            self.print_color(f"⚠️  Erro ao enviar: {e}", 'yellow')
            # Tenta reconectar
            self.connected = False
            time.sleep(1)
            self.connect()
            return False
    
    def create_ascii_graph(self, values, height=10):
        """Cria gráfico ASCII do histórico de temperaturas"""
        if not values:
            return ""
        
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return "─" * len(values)
        
        graph = ""
        for level in range(height, 0, -1):
            threshold = min_val + (max_val - min_val) * (level / height)
            line = ""
            for val in values[-40:]:  # Últimas 40 amostras
                if val >= threshold:
                    line += "█"
                else:
                    line += " "
            graph += line + "\n"
        
        return graph
    
    def format_time(self, seconds):
        """Formata tempo decorrido"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h{minutes:02d}m{secs:02d}s"
        elif minutes > 0:
            return f"{minutes}m{secs:02d}s"
        else:
            return f"{secs}s"
    
    def display_interface(self, temp, cpu_usage, ram_usage, runtime, updates):
        """Mostra interface bonita no terminal"""
        os.system('clear')
        
        # Atualiza histórico
        self.temp_history.append(temp)
        if len(self.temp_history) > self.max_temp_history:
            self.temp_history.pop(0)
        
        # Cores baseadas na temperatura
        if temp < 50:
            temp_color = 'green'
            temp_emoji = '❄️'
        elif temp < 65:
            temp_color = 'yellow'
            temp_emoji = '🌡️'
        elif temp < 80:
            temp_color = 'red'
            temp_emoji = '🔥'
        else:
            temp_color = 'red'
            temp_emoji = '⚠️'
        
        # Cores para uso da CPU
        if cpu_usage < 50:
            cpu_color = 'green'
        elif cpu_usage < 80:
            cpu_color = 'yellow'
        else:
            cpu_color = 'red'
        
        # Interface
        print(f"{self.COLORS['blue']}{'═'*60}{self.COLORS['reset']}")
        print(f"{self.COLORS['purple']}   ⚡ WATERCOOLER MANCER - MONITOR ATIVO ⚡   {self.COLORS['reset']}")
        print(f"{self.COLORS['blue']}{'═'*60}{self.COLORS['reset']}")
        
        # Status
        status_color = 'green' if self.connected else 'red'
        status_text = "CONECTADO ✓" if self.connected else "DESCONECTADO ✗"
        print(f" Status: {self.COLORS[status_color]}{status_text}{self.COLORS['reset']}")
        print(f" Tempo: {runtime} | Atualizações: {updates}")
        print(f"{self.COLORS['gray']}{'─'*60}{self.COLORS['reset']}")
        
        # Dados principais
        print(f" {temp_emoji} {self.COLORS[temp_color]}Temperatura: {temp:5.1f}°C{self.COLORS['reset']}")
        print(f"    Mín: {min(self.temp_history):.1f}°C | Máx: {max(self.temp_history):.1f}°C | Média: {sum(self.temp_history)/len(self.temp_history):.1f}°C")
        print()
        
        print(f" ⚙️  {self.COLORS[cpu_color]}Uso da CPU:  {cpu_usage:5.1f}%{self.COLORS['reset']}")
        print(f" 💾 {self.COLORS['blue']}Uso de RAM:  {ram_usage:5.1f}%{self.COLORS['reset']}")
        print(f"{self.COLORS['gray']}{'─'*60}{self.COLORS['reset']}")
        
        # Gráfico ASCII
        if len(self.temp_history) > 5:
            print(f" {self.COLORS['cyan']}Histórico de Temperatura:{self.COLORS['reset']}")
            graph = self.create_ascii_graph(self.temp_history, height=6)
            print(graph)
        
        # Envio para display
        print(f" {self.COLORS['green']}↗️  Enviando para display: {int(temp)}°C{self.COLORS['reset']}")
        print(f" {self.COLORS['gray']}   Protocolo: [{int(temp)}, 0x00, 0x00]{self.COLORS['reset']}")
        
        print(f"{self.COLORS['blue']}{'═'*60}{self.COLORS['reset']}")
        print(f" {self.COLORS['yellow']}Pressione Ctrl+C para sair{self.COLORS['reset']}")
        print(f"{self.COLORS['blue']}{'═'*60}{self.COLORS['reset']}")
    
    def run(self):
        """Loop principal de monitoramento"""
        if not self.connected:
            self.print_color("⚠️  Executando em modo de teste...", 'yellow')
            time.sleep(2)
        
        start_time = time.time()
        update_count = 0
        
        self.print_color("\n🚀 Iniciando monitoramento em tempo real...", 'green')
        self.print_color("📊 Dados serão atualizados a cada segundo", 'cyan')
        time.sleep(1)
        
        while self.running:
            try:
                # Coleta dados do sistema
                temp = self.get_cpu_temperature()
                cpu_usage = self.get_cpu_usage()
                ram_usage = self.get_ram_usage()
                
                # Formata tempo de execução
                runtime = self.format_time(time.time() - start_time)
                
                # Envia para o display
                if self.connected:
                    success = self.send_to_display(temp)
                    if success:
                        update_count += 1
                
                # Mostra interface
                self.display_interface(temp, cpu_usage, ram_usage, runtime, update_count)
                
                # Aguarda próximo ciclo
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.print_color(f"❌ Erro no loop: {e}", 'red')
                time.sleep(5)

def main():
    """Função principal"""
    # Verifica se é root
    if os.geteuid() != 0:
        print("\n🔒 Este programa precisa de permissões de root")
        print("   Execute com: sudo python3 watercooler_final.py")
        sys.exit(1)
    
    # Cria e executa
    monitor = MancerWaterCoolerFinal()
    monitor.run()
    
    print(f"\n{monitor.COLORS['green']}👋 Programa encerrado{monitor.COLORS['reset']}")

if __name__ == "__main__":
    main()
