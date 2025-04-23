# AutoClick V4
Aplicativo de automação para mouse e teclado

Criado com o objetivo de ajudar pessoas que não possuem mouse e teclado com função de macro. Este programa permite configurar ações automáticas para teclas e botões do mouse com intervalos personalizáveis.

## Principais Características

- Interface gráfica intuitiva e redimensionável
- Automação de cliques do mouse e teclas do teclado
- Dois modos de operação: "segurar para repetir" e "alternar (iniciar/parar)"
- Funções personalizáveis (até 10) com salvamento automático
- Captura automática de teclas e cliques do mouse
- Suporte para uso de botões do mouse como gatilhos

## Como Usar

### Função Principal

1. **Tipo de Entrada**: Escolha entre teclado ou diferentes botões do mouse
2. **Tecla**: Se escolher teclado, digite a tecla desejada
3. **Intervalo**: Defina o tempo em milissegundos entre as repetições
4. **Modo de Operação**:
   - **Segurar para repetir**: A ação é repetida enquanto a tecla/botão estiver pressionada
   - **Alternar**: A primeira vez que pressionar inicia, a segunda vez para
5. Clique em **Iniciar** para ativar e **Parar** para desativar

### Funções Personalizadas

1. Clique em **Adicionar Nova Função**
2. Configure:
   - **Tecla Gatilho**: Tecla ou botão do mouse que ativará a função
     - Clique no campo e pressione a tecla desejada, ou
     - Use os botões de "Mouse como gatilho"
   - **Tipo de Ação**: Escolha entre teclado ou botões do mouse
   - **Tecla/Botão de Ação**: O que será executado quando o gatilho for acionado
   - **Intervalo**: Tempo entre repetições (ms)
   - **Modo de Repetição**: "Contínuo" (repetir enquanto segurar) ou "Uma vez"
3. Clique em **Salvar**
4. Ative todas as funções com o botão **Ativar Todas**

## Dicas e Truques

- Você pode redimensionar as janelas conforme necessário
- Suas configurações são salvas automaticamente
- Para botões do mouse como gatilho, é recomendado usar os botões dedicados no diálogo
- O intervalo mínimo recomendado é 50ms para evitar problemas de desempenho

## Especificações Técnicas

- Desenvolvido em Python com Tkinter
- Utiliza as bibliotecas keyboard e mouse para captura de entrada
- Configurações salvas em formato JSON

## Histórico de Versões

- **V4.0**: Adição de funções personalizadas, captura automática de teclas, suporte para gatilhos de mouse e interface redimensionável
- **V3.0**: Versão inicial com funcionalidades básicas

## Compilação

Para compilar o projeto como um executável:
```
pyinstaller --onefile --noconsole --icon=icon.ico --name "AutoClick V4" --hidden-import keyboard --hidden-import mouse main.py
```
