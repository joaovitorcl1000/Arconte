# IPA

O trato vocal humano não produz uma quantidade infinita de categorias discretas utilizáveis em línguas naturais. O IPA padronizou aproximadamente 107 sons segmentais (consoantes pulmonares, não-pulmonares e vogais), além de modificadores diacríticos.

um espaço vetorial ortogonal (matriz de traços):

    Símbolos-base discretos: O inventário oficial do IPA contém cerca de 107 letras segmentais (consoantes pulmonares, cliques, implosivas, ejetivas e vogais).

    Modificadores (Diacríticos e Suprassegmentais): São cerca de 52 símbolos modificadores (nasalização, ejetivização, aspiração, labialização, comprimento, tom).

Combinando símbolos-base com diacríticos válidos, o número de fones pronunciáveis catalogáveis fica entre 800 e 1.200 segmentos discretos. Criar um arquivo estruturado (ipa_matrix.json) com esses dados é a fundação padrão da linguística computacional.
O padrão acadêmico: Traços Distintivos (Distinctive Features)

Projetos como o Phoible (banco de dados fonológico com milhares de línguas) e a biblioteca Python PanPhon resolvem isso decompondo qualquer símbolo IPA em um vetor binário de traços articulatórios e acústicos (seguindo o modelo de Chomsky & Halle).