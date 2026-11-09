import 'package:flutter/material.dart';

import '../models/world_module.dart';
import '../theme/arconte_theme.dart';
import 'ornaments.dart';

class ModuleTile extends StatefulWidget {
  const ModuleTile({super.key, required this.module, required this.onTap});

  final WorldModule module;
  final VoidCallback onTap;

  @override
  State<ModuleTile> createState() => _ModuleTileState();
}

class _ModuleTileState extends State<ModuleTile> {
  bool hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => hovering = true),
      onExit: (_) => setState(() => hovering = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        decoration: BoxDecoration(
          color: hovering ? const Color(0xFFFFFCF4) : ArconteColors.paper,
          borderRadius: BorderRadius.circular(15),
          border: Border.all(
            color: hovering ? ArconteColors.brass : ArconteColors.border,
            width: hovering ? 1.4 : 1,
          ),
          boxShadow: hovering
              ? [
                  BoxShadow(
                      color: ArconteColors.ink.withValues(alpha: .09),
                      blurRadius: 19,
                      offset: const Offset(0, 7))
                ]
              : [
                  BoxShadow(
                      color: ArconteColors.ink.withValues(alpha: .025),
                      blurRadius: 5,
                      offset: const Offset(0, 2))
                ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            key: Key('module-card-${widget.module.id}'),
            borderRadius: BorderRadius.circular(15),
            onTap: widget.onTap,
            child: Padding(
              padding: const EdgeInsets.all(19),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 46,
                        height: 46,
                        decoration: BoxDecoration(
                          color: ArconteColors.forest,
                          borderRadius: BorderRadius.circular(11),
                        ),
                        child: Icon(widget.module.icon,
                            color: ArconteColors.paleGold, size: 24),
                      ),
                      const Spacer(),
                      const Icon(Icons.arrow_outward_rounded,
                          size: 17, color: ArconteColors.brass),
                    ],
                  ),
                  const SizedBox(height: 15),
                  Text(widget.module.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: ArconteType.cardTitle),
                  const SizedBox(height: 5),
                  Text(widget.module.description,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          color: ArconteColors.secondaryText,
                          fontSize: 12,
                          height: 1.4)),
                  const Spacer(),
                  // Os cartões podem ficar estreitos em grades de 3 colunas.
                  // Nunca deixe os dois rótulos com largura intrínseca ilimitada.
                  LayoutBuilder(builder: (context, constraints) {
                    final status = Text(
                      widget.module.backendImplemented
                          ? '◈  Núcleo criado'
                          : '◇  Planejado',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 10,
                        color: widget.module.backendImplemented
                            ? ArconteColors.brass
                            : ArconteColors.secondaryText,
                        fontWeight: FontWeight.w600,
                      ),
                    );
                    if (constraints.maxWidth < 260) {
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          SmallCaps(widget.module.category,
                              color: ArconteColors.forestLight),
                          const SizedBox(height: 3),
                          status,
                        ],
                      );
                    }
                    return Row(
                      children: [
                        Expanded(
                          child: SmallCaps(widget.module.category,
                              color: ArconteColors.forestLight),
                        ),
                        const SizedBox(width: 8),
                        Flexible(child: status),
                      ],
                    );
                  }),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
