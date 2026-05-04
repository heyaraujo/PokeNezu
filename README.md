# 🐾 PokéNezu - Bot Pokémon estilo Pokétwo (PT-BR)

Bot avançado de Pokémon para Discord inspirado no Pokétwo, totalmente em português 🇧🇷, com sistema completo de captura, batalhas, ginásio, marketplace e imagens personalizadas.

---

## 🚀 Principais Funcionalidades

### 🎮 Gameplay
- `/iniciar` - Começa sua jornada com imagem estilo Pokétwo  
- `/escolher pokemon` - Escolhe seu Pokémon inicial  
- `/capturar nome` - Captura Pokémon selvagens  
- `/pokemon` - Lista seus Pokémon (imagem estilo Pokétwo)  
- `/info nome` - Mostra detalhes do Pokémon  
- `/selecionar indice` - Define Pokémon ativo  
- `/saldo` - Mostra suas moedas  

---

### ⚔️ Sistema de Batalha

- `/batalhar usuario:@player` → PvP por turnos  
- `/batalhar_npc` → batalha contra NPC  
- `/batalhar_ginasio` → batalha contra líder  

💥 Recursos:
- sistema de turnos  
- status (queimado, paralisado)  
- vantagem de tipos real  
- dano baseado em stats reais  
- imagens de batalha estilo Pokétwo (Pillow)  

---

### 🧠 IA de Ataques (Ultra Realista)

✔ ataques oficiais da PokéAPI  
✔ respeita nível do Pokémon  
✔ aprende apenas por **level-up**  
✔ detecta geração automaticamente  
✔ usa versões compatíveis (FireRed, Emerald, etc)  
✔ fallback inteligente por tipo  

---

### 🏆 Sistema de Ginásio

- Spawn automático de líderes  
- Configurável por servidor  

Comando:

/config ginasio #canal

---

### 🌿 Spawn de Pokémon

/config spawn #canal

---

### 🛒 Marketplace

Sistema completo de compra e venda de Pokémon entre jogadores.

---

### 🧾 Multi-Servidor

Cada servidor tem seu próprio progresso (spawn, ginásio, economia).

---

## 🧩 Tecnologias

- Python  
- discord.py  
- Pillow  
- PostgreSQL  
- PokeAPI  

---

## 📦 Instalação

pip install -r requirements.txt

---

## 🔐 Configuração `.env`

DISCORD_TOKEN=SEU_TOKEN  
DATABASE_URL=SUA_DATABASE  
TEMPO_SPAWN_MINUTOS=50  

---

## ▶️ Rodar

python main.py

---

## ⚡ Status

🟢 Pronto para uso
