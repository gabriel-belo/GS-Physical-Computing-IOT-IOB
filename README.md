# GS-Physical-Computing-IOT-IOB
Projeto para Global Solution 2026 1º semestre

Este projeto consiste em um sistema de Visão Computacional desenvolvido para identificar e segmentar focos de incêndio e chamas em vídeos de queimadas. Utilizando processamento digital de imagens tradicional, o algoritmo combina múltiplos espaços de cores e filtragens geométricas para garantir uma detecção robusta e em tempo real.

---

## 🛠️ Descrição da Solução

O algoritmo adota uma abordagem de **pipeline de processamento de imagem em camadas** para isolar as chamas do restante do cenário (fumaça, árvores, terra), minimizando falsos positivos por meio de três etapas principais:

### 1. Construção da Máscara de Cores (Função `build_fire_mask`)
Para mapear os pixels que representam o fogo de forma confiável, o sistema cruza três critérios matemáticos independentes:
* **Critério HSV (Chamas):** Isola os tons de laranja, amarelo e vermelho vivo através de faixas de matrizes circulares no espaço HSV (`cv2.inRange`).
* **Critério do Núcleo da Chama:** Mapeia o centro incandescente do fogo (geralmente branco ou muito claro) identificando regiões de alta luminosidade (*Value*) e baixa saturação (*Saturation*).
* **Critério RGB (Dominância do Vermelho):** Separa os canais BGR da imagem e aplica a regra comparativa $R > G > B$ com limiar mínimo de intensidade. Isso garante que objetos escuros ou cinzentos não sejam confundidos com o fogo.

As máscaras são unidas utilizando operações lógicas bitwise (`cv2.bitwise_or` e `cv2.bitwise_and`).

### 2. Tratamento Morfológico e Redução de Ruído
Após a combinação, a máscara binária passa por operações morfológicas:
* **Abertura (`cv2.MORPH_OPEN`):** Remove pequenos pontos brilhantes isolados (ruídos de compressão ou faíscas distantes).
* **Fechamento (`cv2.MORPH_CLOSE`):** Preenche buracos internos na região da chama, consolidando o bloco principal do incêndio.

### 3. Análise Geométrica dos Contornos (Função `is_fire_contour`)
O sistema localiza os contornos externos dos objetos detectados (`cv2.findContours`) e aplica filtros baseados na física de uma chama:
* **Área Mínima:** Ignora pequenas oscilações de luz ou ruídos remanescentes.
* **Solidez (Convex Hull):** Compara a área do contorno com o seu "envelope convexo" (`cv2.convexHull`). Chamas reais possuem bordas irregulares e dinâmicas, mantendo uma solidez característica entre $0.5$ e $0.9$.
* **Proporção de Tela (Aspect Ratio):** Filtra os blocos avaliando se a relação entre largura e altura condiz com o comportamento verticalizado do fogo.

### 4. Interface Visual e Alertas
O resultado final renderiza um retângulo delimitador (*Bounding Box*) vermelho indicando a área afetada, desenha o contorno exato da chama em verde, projeta o envelope convexo em azul e gera um alerta textual de **"INCÊNDIO DETECTADO"** na tela quando o perigo é confirmado.

---

## 📚 Bibliotecas Utilizadas

O projeto foi construído utilizando as seguintes bibliotecas do ecossistema Python:

* **`OpenCV (opencv-python)`**: Responsável por toda a infraestrutura de leitura do arquivo de vídeo, conversões de espaços de cores (BGR, HSV), filtragens lineares (GaussianBlur), operações lógicas bitwise, morfologia matemática, extração de contornos e renderização gráfica da interface.
* **`NumPy`**: Utilizada para a manipulação rápida e eficiente das matrizes multidimensionais de pixels, definição dos arrays estruturantes dos kernels morfológicos e limites numéricos das máscaras de corte.

---

## 🚀 Instruções Básicas de Execução

### Pré-requisito
Antes de executar o script, certifique-se de ter o Python instalado e as dependências configuradas no seu ambiente. Você pode instalar as bibliotecas necessárias executando:

```bash
pip install opencv-python numpy
```
# Integrantes do Grupo

Enzo Vinycius da Silva Dias 	RM558225

Gabriel Belo 	RM551669

Gustavo Pierre	RM558928

Laura Souza	RM556320

Vinicius Henrique 	RM556908
