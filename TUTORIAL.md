# Tutorial do PokéBR

Este tutorial explica como jogar e administrar o bot.

## 1. Começando

Use:

```txt
/iniciar
```

O bot vai mostrar uma lista de Pokémon iniciais separados por geração.

Depois escolha seu inicial com:

```txt
/escolher pokemon:charmander
```

Exemplos:

```txt
/escolher pokemon:bulbasaur
/escolher pokemon:squirtle
/escolher pokemon:totodile
/escolher pokemon:froakie
```

Cada usuário só pode escolher um inicial.

## 2. Capturando Pokémon

A cada 50 minutos, um Pokémon selvagem aparece no canal configurado.

Quando aparecer, o bot mostra:

- Imagem do Pokémon
- Dica com quantidade de letras
- Nível
- Tipo

Para capturar, use:

```txt
/capturar nome:pikachu
```

Se acertar o nome, o Pokémon vai para sua coleção.

## 3. Vendo seus Pokémon

Use:

```txt
/pokemon
```

O bot mostra seus últimos Pokémon capturados.

## 4. Ver informações de um Pokémon

Use:

```txt
/info nome:pikachu
```

O bot mostra:

- ID da Pokédex
- Tipos
- HP
- Ataque
- Defesa
- Velocidade
- Altura
- Peso
- Imagem

## 5. Moedas

Ao capturar um Pokémon selvagem, você ganha 10 moedas.

Para ver seu saldo:

```txt
/saldo
```

## 6. Testar spawn

Para gerar um Pokémon na hora, use:

```txt
/spawn_teste
```

Esse comando serve para testar se o bot está funcionando.

## 7. Configuração do canal de spawn

No arquivo `.env`, configure:

```env
CANAL_SPAWN_ID=ID_DO_CANAL
```

Para pegar o ID do canal:

1. Ative o modo desenvolvedor no Discord.
2. Clique com botão direito no canal.
3. Clique em “Copiar ID”.
4. Cole no `.env`.

## 8. Configuração do tempo de spawn

O padrão é 50 minutos:

```env
TEMPO_SPAWN_MINUTOS=50
```

## 9. Comandos disponíveis

```txt
/iniciar
/escolher
/tutorial
/capturar
/pokemon
/info
/saldo
/spawn_teste
```

## 10. Observação

Este bot usa a PokeAPI para buscar dados dos Pokémon.


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
