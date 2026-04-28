# PokéBR - Bot estilo Pokétwo em Português

Bot Pokémon para Discord com funções parecidas com o Pokétwo, mas totalmente em português.

## Funções

- `/iniciar` - Mostra os Pokémon iniciais por geração
- `/escolher pokemon` - Escolhe seu Pokémon inicial
- `/capturar nome` - Captura o Pokémon selvagem atual
- `/pokemon` - Lista seus Pokémon
- `/info nome` - Mostra informações de um Pokémon
- `/saldo` - Mostra suas moedas
- `/spawn_teste` - Gera um spawn manual para teste
- `/batalhar` - Batalha contra outro jogador
- `/tutorial` - Mostra o tutorial do bot

## Recursos

- Slash commands `/`
- Spawn automático a cada 50 minutos
- Banco SQLite
- Integração com PokeAPI
- Embeds em português
- Tipos traduzidos para PT-BR

## Instalação

```bash
pip install -r requirements.txt
```

Renomeie `.env.example` para `.env` e configure:

```env
DISCORD_TOKEN=SEU_TOKEN_AQUI
CANAL_SPAWN_ID=ID_DO_CANAL
TEMPO_SPAWN_MINUTOS=50
```

Rode:

```bash
python main.py
```

## Permissões recomendadas no Discord

O bot precisa de:

- Enviar mensagens
- Usar slash commands
- Inserir links
- Anexar arquivos
- Ler histórico de mensagens


## Tutorial

Leia também o arquivo `TUTORIAL.md` ou use `/tutorial` dentro do Discord.


## Batalhas

Use:

```txt
/batalhar usuario:@jogador
```

O bot usa o primeiro Pokémon de cada jogador e calcula o poder com base em:

- nível
- HP
- ataque
- defesa
- velocidade

O vencedor ganha +1 nível.

## Evolução automática

Quando um Pokémon atinge o nível mínimo da evolução, ele evolui automaticamente.

Exemplo:

- Charmander evolui para Charmeleon no nível 16
- Bulbasaur evolui para Ivysaur no nível 16
- Squirtle evolui para Wartortle no nível 16

As evoluções são consultadas pela PokeAPI.
