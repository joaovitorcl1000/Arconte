import 'package:flutter/material.dart';

import '../models/world_module.dart';

/// Espelha apenas os conceitos existentes no Arconte, não lê dados reais.
const List<WorldModule> arconteModules = [
  WorldModule(
    id: 'personagens',
    name: 'Personagens',
    description: 'Identidades, aparência, personalidade e histórias.',
    icon: Icons.person_outline,
    category: 'PESSOAS',
    backendImplemented: true,
    example: 'Artuin Hauck',
  ),
  WorldModule(
    id: 'genealogias',
    name: 'Genealogias',
    description: 'Parentescos, descendências e árvores familiares.',
    icon: Icons.account_tree_outlined,
    category: 'LINHAGENS',
    backendImplemented: true,
    example: 'Linhagem dos Hauck',
  ),
  WorldModule(
    id: 'familias',
    name: 'Casas & Famílias',
    description: 'Casas nobres, clãs, dinastias e seus legados.',
    icon: Icons.home_work_outlined,
    category: 'LINHAGENS',
    backendImplemented: true,
    example: 'Casa Hauck',
  ),
  WorldModule(
    id: 'organizacoes',
    name: 'Organizações',
    description: 'Ordens, facções, guildas e instituições.',
    icon: Icons.shield_outlined,
    category: 'INSTITUIÇÕES',
    backendImplemented: true,
  ),
  WorldModule(
    id: 'religioes',
    name: 'Religiões',
    description: 'Fés, ritos, tradições e seus seguidores.',
    icon: Icons.auto_stories_outlined,
    category: 'CRENÇAS',
    backendImplemented: true,
  ),
  WorldModule(
    id: 'divindades',
    name: 'Divindades',
    description: 'Panteões, entidades, símbolos e domínios.',
    icon: Icons.brightness_5_outlined,
    category: 'CRENÇAS',
    backendImplemented: true,
  ),
  WorldModule(
    id: 'doutrinas',
    name: 'Doutrinas',
    description: 'Crenças, dogmas, ensinamentos e mudanças.',
    icon: Icons.menu_book_outlined,
    category: 'CRENÇAS',
    backendImplemented: true,
  ),
  WorldModule(
    id: 'cronologias',
    name: 'Cronologias',
    description: 'Eras, marcos históricos e linhas do tempo.',
    icon: Icons.hourglass_bottom_outlined,
    category: 'TEMPO',
    backendImplemented: false,
  ),
  WorldModule(
    id: 'lugares',
    name: 'Lugares & Mapas',
    description: 'Terras, regiões, cidades e cenários.',
    icon: Icons.explore_outlined,
    category: 'TERRITÓRIOS',
    backendImplemented: false,
  ),
  WorldModule(
    id: 'reinos',
    name: 'Reinos & Nações',
    description: 'Estados, fronteiras, governos e alianças.',
    icon: Icons.flag_outlined,
    category: 'TERRITÓRIOS',
    backendImplemented: false,
  ),
  WorldModule(
    id: 'especies',
    name: 'Espécies',
    description: 'Povos, criaturas e formas de vida.',
    icon: Icons.pets_outlined,
    category: 'MUNDO',
    backendImplemented: false,
  ),
  WorldModule(
    id: 'artefatos',
    name: 'Artefatos',
    description: 'Relíquias, objetos, armas e tesouros.',
    icon: Icons.diamond_outlined,
    category: 'MUNDO',
    backendImplemented: false,
  ),
];

WorldModule? findModule(String id) {
  for (final module in arconteModules) {
    if (module.id == id) return module;
  }
  return null;
}
