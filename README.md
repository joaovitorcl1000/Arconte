# Projeto Arconte

> **A plataforma definitiva e modular de Worldbuilding para a comunidade brasileira.**

O **Arconte** (nome provisório) é uma plataforma estilo "wiki" focada em escritores, mestres de RPG e *worldbuilders*. Nascido da necessidade de fugir de interfaces poluídas e sistemas pesados (como o World Anvil), o projeto foca em organização limpa, construção modular e facilidade de uso, com suporte nativo à língua portuguesa e à comunidade do Brasil.

---

## 🏗️ Arquitetura do Sistema

O projeto adota uma arquitetura moderna e multiplataforma, separando a aplicação principal (o dashboard do usuário) da página de marketing para otimização de buscas (SEO).

### 1. Frontend (A Ferramenta)
* **Linguagem / Framework:** Dart com **Flutter**.
* **Motivo:** Permite compilar o exato mesmo código para Web (SPA), Desktop (Windows/Linux/Mac) e Mobile (iOS/Android). Ideal para interfaces ricas, painéis complexos e renderização de mapas e gráficos.

### 2. Backend & Banco de Dados
* **Linguagem / Framework:** Python com **FastAPI**.
* **Motivo:** Excelente performance para lidar com lógica complexa, cruzamento de dados de *lore* e algoritmos de busca.
* **Autenticação & Realtime:** **Firebase** (Auth e Firestore para dados que precisam de sincronização em tempo real entre dispositivos).

### 3. Landing Page (Marketing e SEO)
* **Stack:** HTML/CSS/JS simples (ou frameworks como Astro/Next.js).
* **Motivo:** Como o Flutter Web renderiza tudo em Canvas/WebGL (o que os robôs do Google não conseguem ler), a página inicial pública será feita em web tradicional para garantir indexação no Google. O Flutter será chamado apenas no subdomínio da aplicação (ex: `app.Arconte.com.br`).

---

## 📦 Bibliotecas e Ferramentas Chave (Flutter)

Para acelerar o desenvolvimento, utilizaremos pacotes já validados pela comunidade Dart:

| Recurso | Pacote Sugerido | Descrição |
| :--- | :--- | :--- |
| **Editor de Artigos (Wiki)** | `flutter_quill` | Editor *Rich Text* poderoso (estilo Notion). Essencial para formatar rituais, regras de sistemas de magia e vocabulários (ex: gramática do idioma *Lício*). |
| **Árvores Genealógicas** | `graphview` ou `CustomPaint` | Para renderizar dinamicamente nós e arestas baseados nas relações de parentesco do banco de dados (ex: Dinastias do Império de Arcum). |
| **Mapas Interativos** | `flutter_map` | Para criar o Atlas do mundo. Suporta *tiles* (fatias de imagens), permitindo dar zoom em mapas de alta resolução e adicionar *pins* interativos. |
| **Gerenciamento de Estado** | `riverpod` ou `bloc` | Para manter o dashboard responsivo e garantir que a atualização de um personagem reflita automaticamente nos outros módulos abertos. |

---

## 🚀 Estratégia de Desenvolvimento (Roadmap)

### Fase 1: Fundação & Modelagem (Atual)
- [ ] Definir o nome oficial e branding.
- [ ] Modelar a estrutura do Banco de Dados (Usuários, Universos, Artigos, Categorias, Relações).
- [ ] Desenhar o fluxo de telas no Figma (Wireframes básicos focados em UX limpa).

### Fase 2: O MVP (Produto Mínimo Viável)
- [ ] Configurar Firebase Auth.
- [ ] Criar o CRUD (Criar, Ler, Atualizar, Deletar) de categorias e artigos usando o `flutter_quill`.
- [ ] Implementar sistema de links cruzados (mencionar um artigo dentro de outro).

### Fase 3: Módulos Especiais
- [ ] Módulo de Famílias (Árvore Genealógica automatizada).
- [ ] Módulo de Mapas (Upload de mapa e marcadores).

### Fase 4: Lançamento
- [ ] Publicar a Landing Page estática.
- [ ] Hospedar o app Flutter Web.
- [ ] Divulgar para a comunidade brasileira (Reddit, fóruns, *Worldbuilding para Todos*).
