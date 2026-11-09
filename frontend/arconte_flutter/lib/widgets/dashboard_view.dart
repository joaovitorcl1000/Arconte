import 'package:flutter/material.dart';

import '../data/module_catalog.dart';
import '../models/world_module.dart';
import '../theme/arconte_theme.dart';
import 'module_tile.dart';
import 'ornaments.dart';

class DashboardView extends StatelessWidget {
  const DashboardView({super.key, required this.search, required this.onOpen});

  final String search;
  final ValueChanged<String> onOpen;

  @override
  Widget build(BuildContext context) {
    final searchLower = search.toLowerCase().trim();
    final ready = arconteModules
        .where((module) =>
            module.backendImplemented && _matches(module, searchLower))
        .toList();
    final future = arconteModules
        .where((module) =>
            !module.backendImplemented && _matches(module, searchLower))
        .toList();
    return LayoutBuilder(builder: (context, constraints) {
      final wide = constraints.maxWidth >= 1020;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SmallCaps('BIBLIOTECA / MUNDO DEMONSTRATIVO',
              color: ArconteColors.forestLight),
          const SizedBox(height: 10),
          const Text('Onde os mundos ganham vida.', style: ArconteType.display),
          const SizedBox(height: 13),
          const Text(
            'Um ateliê para guardar linhagens, crenças, reinos e todas as histórias que ainda serão contadas.',
            style: TextStyle(color: ArconteColors.secondaryText, fontSize: 14),
          ),
          const SizedBox(height: 25),
          _WorldHero(onExplore: () => onOpen('personagens')),
          const SizedBox(height: 35),
          if (wide)
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                    child: _CatalogSection(
                  title: 'Os pilares do seu mundo',
                  subtitle: 'Coleções prontas para receber suas criações.',
                  modules: ready,
                  future: future,
                  onOpen: onOpen,
                )),
                const SizedBox(width: 23),
                const SizedBox(width: 282, child: _CodexAside()),
              ],
            )
          else ...[
            _CatalogSection(
              title: 'Os pilares do seu mundo',
              subtitle: 'Coleções prontas para receber suas criações.',
              modules: ready,
              future: future,
              onOpen: onOpen,
            ),
            const SizedBox(height: 25),
            const _CodexAside(),
          ],
          const SizedBox(height: 20),
          Center(
              child: Text('ARCONTE  ·  O MUNDO É SEU PARA ESCREVER',
                  style: TextStyle(
                      letterSpacing: 2.2,
                      fontSize: 9,
                      color:
                          ArconteColors.secondaryText.withValues(alpha: .8)))),
          const SizedBox(height: 15),
        ],
      );
    });
  }

  bool _matches(WorldModule module, String q) {
    return q.isEmpty ||
        module.name.toLowerCase().contains(q) ||
        module.description.toLowerCase().contains(q) ||
        module.category.toLowerCase().contains(q);
  }
}

class _WorldHero extends StatelessWidget {
  const _WorldHero({required this.onExplore});

  final VoidCallback onExplore;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, limits) {
      final compact = limits.maxWidth < 540;
      return ClipRRect(
        borderRadius: BorderRadius.circular(19),
        child: Container(
          height: compact ? 297 : 263,
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF23483F), Color(0xFF13282B), Color(0xFF102024)],
            ),
          ),
          child: Stack(
            children: [
              const Positioned.fill(
                  child: CustomPaint(painter: CitadelPainter())),
              Positioned(
                top: 14,
                bottom: 14,
                left: 14,
                right: 14,
                child: Container(
                    decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(11),
                  border: Border.all(
                      color: ArconteColors.paleGold.withValues(alpha: .30)),
                )),
              ),
              Padding(
                padding: EdgeInsets.fromLTRB(compact ? 23 : 38, 35, 20, 26),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 480),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SmallCaps('UM UNIVERSO À SUA ESPERA',
                            color: ArconteColors.paleGold),
                        const SizedBox(height: 11),
                        Text('Escreva as lendas.\nGuarde os legados.',
                            style: TextStyle(
                                fontFamily: 'serif',
                                fontSize: compact ? 28 : 33,
                                height: 1.13,
                                fontWeight: FontWeight.w600,
                                color: ArconteColors.paper)),
                        const SizedBox(height: 9),
                        Text(
                            'Pessoas, casas, fés e instituições em um só códice.',
                            style: TextStyle(
                                fontSize: 12.5,
                                color: ArconteColors.paper
                                    .withValues(alpha: .78))),
                        const SizedBox(height: 19),
                        OutlinedButton.icon(
                          onPressed: onExplore,
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: ArconteColors.brass),
                            backgroundColor: ArconteColors.paleGold,
                            foregroundColor: ArconteColors.ink,
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 12),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8)),
                          ),
                          icon: const Icon(Icons.arrow_forward, size: 16),
                          label: const Text('Explorar o códice',
                              style: TextStyle(
                                  fontSize: 12, fontWeight: FontWeight.w800)),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    });
  }
}

class _CatalogSection extends StatelessWidget {
  const _CatalogSection({
    required this.title,
    required this.subtitle,
    required this.modules,
    required this.future,
    required this.onOpen,
  });

  final String title;
  final String subtitle;
  final List<WorldModule> modules;
  final List<WorldModule> future;
  final ValueChanged<String> onOpen;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      final cols = constraints.maxWidth >= 880
          ? 3
          : constraints.maxWidth >= 500
              ? 2
              : 1;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: ArconteType.heading),
          const SizedBox(height: 6),
          Text(subtitle,
              style: const TextStyle(
                  fontSize: 12.5, color: ArconteColors.secondaryText)),
          const SizedBox(height: 15),
          const DecorativeRule(width: 76),
          const SizedBox(height: 20),
          if (modules.isEmpty)
            const _NoSearchResults()
          else
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: modules.length,
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: cols,
                crossAxisSpacing: 13,
                mainAxisSpacing: 13,
                mainAxisExtent: 211,
              ),
              itemBuilder: (_, index) {
                final module = modules[index];
                return ModuleTile(
                    module: module, onTap: () => onOpen(module.id));
              },
            ),
          if (future.isNotEmpty) ...[
            const SizedBox(height: 29),
            const SmallCaps('ALÉM DO HORIZONTE',
                color: ArconteColors.forestLight),
            const SizedBox(height: 13),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final module in future)
                  ActionChip(
                    tooltip: 'Módulo planejado',
                    avatar: Icon(module.icon,
                        size: 17, color: ArconteColors.forest),
                    label:
                        Text(module.name, style: const TextStyle(fontSize: 12)),
                    onPressed: () => onOpen(module.id),
                    backgroundColor: ArconteColors.softPaper,
                    side: const BorderSide(color: ArconteColors.border),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(9)),
                  ),
              ],
            ),
          ],
        ],
      );
    });
  }
}

class _NoSearchResults extends StatelessWidget {
  const _NoSearchResults();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(25),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: ArconteColors.border),
        color: ArconteColors.paper,
      ),
      child: const Row(children: [
        Icon(Icons.search_off_outlined, color: ArconteColors.brass),
        SizedBox(width: 12),
        Expanded(
            child: Text('Nenhum módulo corresponde à pesquisa.',
                style: TextStyle(color: ArconteColors.secondaryText))),
      ]),
    );
  }
}

class _CodexAside extends StatelessWidget {
  const _CodexAside();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(21, 23, 21, 22),
      decoration: BoxDecoration(
        color: const Color(0xFFE8DECB),
        border: Border.all(color: const Color(0xFFCFBEA1)),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SmallCaps('CÓDICE DE EXEMPLO',
              color: ArconteColors.forestLight),
          const SizedBox(height: 13),
          const Text('Sarnília',
              style: TextStyle(
                  color: ArconteColors.ink,
                  fontFamily: 'serif',
                  fontSize: 32,
                  fontWeight: FontWeight.w600)),
          const SizedBox(height: 3),
          const Text('As crônicas do Morro do Falcão',
              style: TextStyle(
                  color: ArconteColors.secondaryText, fontSize: 12.5)),
          const SizedBox(height: 22),
          Container(
            width: double.infinity,
            height: 154,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(10),
              color: const Color(0xFF314E45),
              border:
                  Border.all(color: ArconteColors.brass.withValues(alpha: .4)),
            ),
            clipBehavior: Clip.antiAlias,
            child: const Stack(
              children: [
                Positioned.fill(child: CustomPaint(painter: CitadelPainter())),
                Center(
                    child: Icon(Icons.castle_outlined,
                        color: ArconteColors.paleGold, size: 45)),
              ],
            ),
          ),
          const SizedBox(height: 21),
          const Row(children: [
            Icon(Icons.hourglass_empty_outlined,
                size: 16, color: ArconteColors.brass),
            SizedBox(width: 9),
            Text('Ano 67 depois da Unificação',
                style: TextStyle(fontSize: 12, color: ArconteColors.text)),
          ]),
          const SizedBox(height: 18),
          Divider(color: ArconteColors.brass.withValues(alpha: .45)),
          const SizedBox(height: 17),
          const Text(
              '“Uma árvore guarda os nomes.\nUma história preserva as almas.”',
              style: TextStyle(
                  fontFamily: 'serif',
                  fontSize: 17,
                  fontStyle: FontStyle.italic,
                  color: ArconteColors.forest,
                  height: 1.45)),
          const SizedBox(height: 20),
          const Text(
              'Este painel é uma composição visual baseada no seu mundo. '
              'Os dados do projeto Python ainda não estão conectados.',
              style: TextStyle(
                  fontSize: 11.5,
                  color: ArconteColors.secondaryText,
                  height: 1.5)),
          const SizedBox(height: 12),
          const DecorativeRule(width: 54),
        ],
      ),
    );
  }
}
