import 'package:flutter/material.dart';

import '../data/module_catalog.dart';
import 'characters/characters_screen.dart';
import '../models/world_module.dart';
import '../services/character_api.dart';
import '../theme/arconte_theme.dart';
import '../widgets/dashboard_view.dart';
import '../widgets/module_view.dart';
import '../widgets/navigation_panel.dart';

class WorkspaceScreen extends StatefulWidget {
  const WorkspaceScreen({super.key, this.characterApi});

  /// Fornecido opcionalmente por testes ou futuras configurações.
  final CharacterApi? characterApi;

  @override
  State<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends State<WorkspaceScreen> {
  String? selectedId;
  String search = '';
  final TextEditingController searchController = TextEditingController();

  @override
  void dispose() {
    searchController.dispose();
    super.dispose();
  }

  void goHome() => setState(() => selectedId = null);

  void openModule(String id) {
    if (findModule(id) == null) return;
    setState(() => selectedId = id);
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      final compact = constraints.maxWidth < 960;
      final WorldModule? module =
          selectedId == null ? null : findModule(selectedId!);
      return Scaffold(
        drawer: compact
            ? Drawer(
                width: 272,
                child: Builder(builder: (drawerContext) {
                  return NavigationPanel(
                    width: 272,
                    selectedId: selectedId,
                    onHome: () {
                      goHome();
                      Navigator.of(drawerContext).pop();
                    },
                    onSelect: (id) {
                      openModule(id);
                      Navigator.of(drawerContext).pop();
                    },
                  );
                }),
              )
            : null,
        body: Row(children: [
          if (!compact)
            NavigationPanel(
              selectedId: selectedId,
              onHome: goHome,
              onSelect: openModule,
            ),
          Expanded(
            child: Column(children: [
              Builder(builder: (bodyContext) {
                return _WorkspaceHeader(
                  compact: compact,
                  sectionName: module?.name,
                  charactersSelected: module?.id == 'personagens',
                  onMenu: () => Scaffold.of(bodyContext).openDrawer(),
                  controller: searchController,
                  onSearch: (value) => setState(() => search = value),
                );
              }),
              Expanded(
                child: SingleChildScrollView(
                  key: ValueKey(selectedId ?? 'dashboard'),
                  padding: EdgeInsets.symmetric(
                    horizontal: compact ? 22 : 40,
                    vertical: compact ? 30 : 37,
                  ),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1380),
                      child: module == null
                          ? DashboardView(search: search, onOpen: openModule)
                          : module.id == 'personagens'
                              ? CharactersScreen(
                                  onBack: goHome, api: widget.characterApi)
                              : ModuleView(module: module, onBack: goHome),
                    ),
                  ),
                ),
              ),
            ]),
          ),
        ]),
      );
    });
  }
}

class _WorkspaceHeader extends StatelessWidget {
  const _WorkspaceHeader({
    required this.compact,
    required this.sectionName,
    required this.charactersSelected,
    required this.onMenu,
    required this.controller,
    required this.onSearch,
  });

  final bool compact;
  final String? sectionName;
  final bool charactersSelected;
  final VoidCallback onMenu;
  final TextEditingController controller;
  final ValueChanged<String> onSearch;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 75,
      padding: EdgeInsets.symmetric(horizontal: compact ? 17 : 39),
      decoration: const BoxDecoration(
        color: ArconteColors.paper,
        border: Border(bottom: BorderSide(color: ArconteColors.border)),
      ),
      child: LayoutBuilder(builder: (context, box) {
        final tight = box.maxWidth < 590;
        return Row(children: [
          if (compact) ...[
            IconButton(
              tooltip: 'Abrir menu',
              onPressed: onMenu,
              icon: const Icon(Icons.menu, color: ArconteColors.forest),
            ),
            const SizedBox(width: 4),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('SEU CÓDICE',
                    style: TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.8,
                        color: ArconteColors.brass)),
                const SizedBox(height: 3),
                Text(
                    sectionName == null
                        ? 'Sarnília  /  Visão geral'
                        : 'Sarnília  /  $sectionName',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        color: ArconteColors.ink,
                        fontSize: 14,
                        fontWeight: FontWeight.w700)),
              ],
            ),
          ),
          if (!tight) ...[
            SizedBox(
              width: box.maxWidth >= 930 ? 300 : 210,
              height: 39,
              child: TextField(
                controller: controller,
                onChanged: onSearch,
                decoration: InputDecoration(
                  hintText: 'Buscar módulos...',
                  prefixIcon: const Icon(Icons.search,
                      size: 19, color: ArconteColors.secondaryText),
                  suffixIcon: controller.text.isEmpty
                      ? null
                      : IconButton(
                          tooltip: 'Limpar pesquisa',
                          icon: const Icon(Icons.close, size: 15),
                          onPressed: () {
                            controller.clear();
                            onSearch('');
                          },
                        ),
                  contentPadding: const EdgeInsets.symmetric(vertical: 8),
                ),
              ),
            ),
            const SizedBox(width: 17),
          ],
          if (!tight)
            Container(
              height: 29,
              padding: const EdgeInsets.symmetric(horizontal: 11),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: ArconteColors.softPaper,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: ArconteColors.border),
              ),
              child: const Text('67 d.U.',
                  style: TextStyle(
                      color: ArconteColors.forest,
                      fontSize: 11,
                      fontWeight: FontWeight.w800)),
            ),
          const SizedBox(width: 13),
          Tooltip(
            message: charactersSelected
                ? 'Personagens: dados consultados na API local do Arconte'
                : 'Painel demonstrativo: demais módulos aguardam integração',
            child: Container(
              width: 35,
              height: 35,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: ArconteColors.forest,
                borderRadius: BorderRadius.circular(11),
                border: Border.all(color: ArconteColors.brass, width: 1),
              ),
              child: const Text('S',
                  style: TextStyle(
                      fontFamily: 'serif',
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: ArconteColors.paleGold)),
            ),
          ),
        ]);
      }),
    );
  }
}
