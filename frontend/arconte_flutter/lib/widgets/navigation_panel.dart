import 'package:flutter/material.dart';

import '../data/module_catalog.dart';
import '../theme/arconte_theme.dart';
import 'ornaments.dart';

class NavigationPanel extends StatelessWidget {
  const NavigationPanel({
    super.key,
    required this.selectedId,
    required this.onHome,
    required this.onSelect,
    this.width = 252,
  });

  final String? selectedId;
  final VoidCallback onHome;
  final ValueChanged<String> onSelect;
  final double width;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      color: ArconteColors.night,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(23, 26, 20, 23),
              child: Row(
                children: [
                  Container(
                    width: 43,
                    height: 48,
                    decoration: BoxDecoration(
                      color: ArconteColors.forest,
                      border: Border.all(
                          color: ArconteColors.brass.withValues(alpha: .7)),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.change_history_outlined,
                        color: ArconteColors.paleGold, size: 30),
                  ),
                  const SizedBox(width: 12),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('ARCONTE',
                          style: TextStyle(
                            fontFamily: 'serif',
                            fontSize: 22,
                            letterSpacing: 2.2,
                            color: ArconteColors.paper,
                            fontWeight: FontWeight.w700,
                          )),
                      SizedBox(height: 2),
                      SmallCaps('ATELIÊ DE MUNDOS',
                          color: ArconteColors.paleGold),
                    ],
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Divider(
                  color: ArconteColors.paleGold.withValues(alpha: .22),
                  height: 1),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(13, 23, 13, 20),
                children: [
                  const Padding(
                    padding: EdgeInsets.only(left: 14, bottom: 11),
                    child: SmallCaps('ESCRITÓRIO', color: ArconteColors.moss),
                  ),
                  _NavigationItem(
                    label: 'Visão geral',
                    icon: Icons.dashboard_outlined,
                    selected: selectedId == null,
                    onTap: onHome,
                  ),
                  const SizedBox(height: 27),
                  const Padding(
                    padding: EdgeInsets.only(left: 14, bottom: 11),
                    child: SmallCaps('CRIAÇÃO', color: ArconteColors.moss),
                  ),
                  for (final module
                      in arconteModules.where((m) => m.backendImplemented))
                    _NavigationItem(
                      label: module.name,
                      icon: module.icon,
                      selected: selectedId == module.id,
                      onTap: () => onSelect(module.id),
                    ),
                  const SizedBox(height: 27),
                  const Padding(
                    padding: EdgeInsets.only(left: 14, bottom: 11),
                    child: SmallCaps('HORIZONTES', color: ArconteColors.moss),
                  ),
                  for (final module
                      in arconteModules.where((m) => !m.backendImplemented))
                    _NavigationItem(
                      label: module.name,
                      icon: module.icon,
                      selected: selectedId == module.id,
                      muted: true,
                      onTap: () => onSelect(module.id),
                    ),
                ],
              ),
            ),
            Container(
              width: double.infinity,
              margin: const EdgeInsets.fromLTRB(15, 4, 15, 18),
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: ArconteColors.forest.withValues(alpha: .48),
                borderRadius: BorderRadius.circular(13),
                border: Border.all(
                    color: ArconteColors.brass.withValues(alpha: .25)),
              ),
              child: const Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.auto_stories_outlined,
                      color: ArconteColors.paleGold, size: 20),
                  SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Sua história começa aqui',
                            style: TextStyle(
                                color: ArconteColors.paper,
                                fontSize: 12,
                                fontWeight: FontWeight.w700)),
                        SizedBox(height: 6),
                        Text('Prévia visual • sem dados conectados',
                            style: TextStyle(
                                color: ArconteColors.moss,
                                fontSize: 11,
                                height: 1.4)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavigationItem extends StatelessWidget {
  const _NavigationItem({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
    this.muted = false,
  });

  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  final bool muted;

  @override
  Widget build(BuildContext context) {
    final color = selected
        ? ArconteColors.paleGold
        : muted
            ? ArconteColors.moss
            : ArconteColors.paper.withValues(alpha: .8);
    return Padding(
      padding: const EdgeInsets.only(bottom: 3),
      child: Material(
        color: selected ? ArconteColors.forest : Colors.transparent,
        borderRadius: BorderRadius.circular(9),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(9),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 13),
            decoration: BoxDecoration(
              border: selected
                  ? const Border(
                      left: BorderSide(color: ArconteColors.brass, width: 3))
                  : null,
            ),
            child: Row(
              children: [
                Icon(icon, size: 19, color: color),
                const SizedBox(width: 13),
                Expanded(
                  child: Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                        fontSize: 12.5,
                        color: color,
                        fontWeight:
                            selected ? FontWeight.w700 : FontWeight.w500),
                  ),
                ),
                if (muted)
                  const Icon(Icons.lock_clock_outlined,
                      size: 12, color: ArconteColors.moss),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
