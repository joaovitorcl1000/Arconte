import 'package:flutter/material.dart';

import '../models/world_module.dart';
import '../theme/arconte_theme.dart';
import 'ornaments.dart';

class ModuleView extends StatelessWidget {
  const ModuleView({super.key, required this.module, required this.onBack});

  final WorldModule module;
  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      final wide = constraints.maxWidth > 800;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextButton.icon(
            onPressed: onBack,
            icon: const Icon(Icons.arrow_back, size: 17),
            label: const Text('Voltar ao códice'),
            style: TextButton.styleFrom(foregroundColor: ArconteColors.forest),
          ),
          const SizedBox(height: 22),
          SmallCaps('MÓDULOS / ${module.category}',
              color: ArconteColors.forestLight),
          const SizedBox(height: 12),
          Text(module.name, style: ArconteType.display),
          const SizedBox(height: 10),
          Text(module.description,
              style: const TextStyle(
                  fontSize: 15, color: ArconteColors.secondaryText)),
          const SizedBox(height: 25),
          const DecorativeRule(width: 118),
          const SizedBox(height: 28),
          if (wide)
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Expanded(flex: 3, child: _MainPlaceholder(module: module)),
              const SizedBox(width: 20),
              Expanded(flex: 2, child: _ModuleNotes(module: module)),
            ])
          else ...[
            _MainPlaceholder(module: module),
            const SizedBox(height: 20),
            _ModuleNotes(module: module),
          ],
        ],
      );
    });
  }
}

class _MainPlaceholder extends StatelessWidget {
  const _MainPlaceholder({required this.module});

  final WorldModule module;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minHeight: 420),
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: ArconteColors.paper,
        borderRadius: BorderRadius.circular(17),
        border: Border.all(color: ArconteColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const Align(
              alignment: Alignment.topLeft,
              child:
                  SmallCaps('A BIBLIOTECA', color: ArconteColors.forestLight)),
          const SizedBox(height: 49),
          Container(
            width: 96,
            height: 96,
            decoration: BoxDecoration(
              color: ArconteColors.softPaper,
              border:
                  Border.all(color: ArconteColors.brass.withValues(alpha: .65)),
              shape: BoxShape.circle,
            ),
            child: Icon(module.icon, size: 47, color: ArconteColors.forest),
          ),
          const SizedBox(height: 24),
          Text('Sua biblioteca de ${module.name.toLowerCase()}',
              textAlign: TextAlign.center,
              style: ArconteType.heading.copyWith(fontSize: 25)),
          const SizedBox(height: 13),
          const Text(
              'Um espaço reservado para organizar seus registros, '
              'explorar conexões e contar novas histórias.',
              textAlign: TextAlign.center,
              style: TextStyle(
                  color: ArconteColors.secondaryText,
                  height: 1.5,
                  fontSize: 13)),
          const SizedBox(height: 22),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFFF2E8D7),
              borderRadius: BorderRadius.circular(9),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.link_off_outlined,
                  color: ArconteColors.crimson, size: 16),
              const SizedBox(width: 9),
              Flexible(
                  child: Text(
                      module.backendImplemented
                          ? 'Módulo Python existente · integração pendente'
                          : 'Módulo Python planejado',
                      style: const TextStyle(
                          fontSize: 11.5,
                          color: ArconteColors.crimson,
                          fontWeight: FontWeight.w700))),
            ]),
          ),
          const SizedBox(height: 36),
          const DecorativeRule(width: 74),
        ],
      ),
    );
  }
}

class _ModuleNotes extends StatelessWidget {
  const _ModuleNotes({required this.module});

  final WorldModule module;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(25),
      decoration: BoxDecoration(
        color: const Color(0xFFE6DCC8),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: const Color(0xFFCEBEA3)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SmallCaps('NOTAS DO ARQUITETO', color: ArconteColors.forestLight),
        const SizedBox(height: 16),
        const Text('O que vem depois?', style: ArconteType.cardTitle),
        const SizedBox(height: 18),
        const _NoteRow('01', 'Conectar este espaço à API Python.'),
        const SizedBox(height: 17),
        const _NoteRow('02', 'Mostrar os registros do mundo selecionado.'),
        const SizedBox(height: 17),
        const _NoteRow('03', 'Habilitar criação, edição e vínculos.'),
        if (module.example != null) ...[
          const SizedBox(height: 21),
          Divider(color: ArconteColors.brass.withValues(alpha: .5)),
          const SizedBox(height: 14),
          const SmallCaps('EXEMPLO DA SUA HISTÓRIA',
              color: ArconteColors.forestLight),
          const SizedBox(height: 9),
          Text(module.example!,
              style: const TextStyle(
                  color: ArconteColors.ink, fontFamily: 'serif', fontSize: 19)),
          const SizedBox(height: 5),
          const Text('Referência ilustrativa, não carregada do JSON.',
              style:
                  TextStyle(fontSize: 11, color: ArconteColors.secondaryText)),
        ],
      ]),
    );
  }
}

class _NoteRow extends StatelessWidget {
  const _NoteRow(this.number, this.label);

  final String number;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(number,
          style: const TextStyle(
              fontFamily: 'serif', fontSize: 19, color: ArconteColors.brass)),
      const SizedBox(width: 13),
      Expanded(
          child: Text(label,
              style: const TextStyle(
                  color: ArconteColors.text, fontSize: 12.5, height: 1.5))),
    ]);
  }
}
