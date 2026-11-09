import 'dart:convert';

import 'package:flutter/material.dart';

import '../../models/character.dart';
import '../../services/character_api.dart';
import '../../theme/arconte_theme.dart';
import '../../widgets/ornaments.dart';

/// Ficha individual: busca sempre a versão completa via GET /api/characters/{id}.
///
/// Não recebe uma ficha resumida como verdade: o backend é a fonte dos dados.
/// Não cria um Scaffold porque o WorkspaceScreen já fornece a estrutura geral.
///
/// Quando [api] é fornecido, o componente não encerra o cliente HTTP externo.
class CharacterDetails extends StatefulWidget {
  const CharacterDetails({
    super.key,
    required this.characterId,
    this.api,
    this.onBack,
  });

  final String characterId;
  final CharacterApi? api;
  final VoidCallback? onBack;

  @override
  State<CharacterDetails> createState() => _CharacterDetailsState();
}

class _CharacterDetailsState extends State<CharacterDetails> {
  late final CharacterApi _api;
  late final bool _ownsApi;
  Character? _character;
  String? _error;
  bool _loading = true;
  int _generation = 0;

  @override
  void initState() {
    super.initState();
    _ownsApi = widget.api == null;
    _api = widget.api ?? CharacterApi();
    _loadCharacter();
  }

  @override
  void didUpdateWidget(covariant CharacterDetails oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.characterId != widget.characterId) _loadCharacter();
  }

  @override
  void dispose() {
    _generation++;
    if (_ownsApi) _api.dispose();
    super.dispose();
  }

  Future<void> _loadCharacter() async {
    final generation = ++_generation;
    setState(() {
      _character = null;
      _loading = true;
      _error = null;
    });
    try {
      final character = await _api.getCharacter(widget.characterId);
      if (!mounted || generation != _generation) return;
      setState(() {
        _character = character;
        _loading = false;
      });
    } catch (error) {
      if (!mounted || generation != _generation) return;
      setState(() {
        _error = error is CharacterApiException
            ? error.message
            : 'Não foi possível consultar a ficha. Verifique sua conexão.';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.onBack != null) ...[
          TextButton.icon(
            onPressed: widget.onBack,
            icon: const Icon(Icons.arrow_back, size: 17),
            label: const Text('Voltar aos personagens'),
            style: TextButton.styleFrom(foregroundColor: ArconteColors.forest),
          ),
          const SizedBox(height: 21),
        ],
        const SmallCaps('BIBLIOTECA / PESSOAS / FICHA',
            color: ArconteColors.forestLight),
        const SizedBox(height: 12),
        if (_loading)
          const _StatusCard(
            title: 'Consultando os anais...',
            description: 'Carregando a ficha completa do personagem.',
            loading: true,
          )
        else if (_error != null)
          _StatusCard(
            title: 'Não foi possível abrir esta ficha',
            description: _error!,
            onRetry: _loadCharacter,
          )
        else if (_character != null)
          _characterBody(_character!),
        const SizedBox(height: 30),
      ],
    );
  }

  Widget _characterBody(Character person) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _CharacterHero(character: person, onRefresh: _loadCharacter),
        const SizedBox(height: 27),
        const DecorativeRule(width: 115),
        const SizedBox(height: 27),
        LayoutBuilder(builder: (context, constraints) {
          // Cartões crescem naturalmente com o conteúdo; nunca há campos
          // truncados ou colunas de altura fixa.
          final wide = constraints.maxWidth >= 850;
          if (!wide) {
            return Column(children: [
              _identity(person),
              const SizedBox(height: 17),
              _physical(person.physical!),
              const SizedBox(height: 17),
              _personality(person.personality!),
              const SizedBox(height: 17),
              _social(person.social!),
              const SizedBox(height: 17),
              _history(person.history!, person.biography),
            ]);
          }
          return Column(children: [
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Expanded(child: _identity(person)),
              const SizedBox(width: 17),
              Expanded(child: _physical(person.physical!)),
            ]),
            const SizedBox(height: 17),
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Expanded(child: _personality(person.personality!)),
              const SizedBox(width: 17),
              Expanded(child: _social(person.social!)),
            ]),
            const SizedBox(height: 17),
            _history(person.history!, person.biography),
          ]);
        }),
      ],
    );
  }

  Widget _identity(Character person) => _SectionCard(
        icon: Icons.badge_outlined,
        eyebrow: 'I · IDENTIDADE',
        title: 'O nome nos registros',
        children: [
          _Fact('Nome', person.name),
          _Fact('Sobrenome', person.surname),
          _Fact('Nome completo', person.fullName),
          _Fact('Gênero', person.gender),
          _Fact('Nascimento', _year(person.birthYear)),
          _Fact('Falecimento', _year(person.deathYear)),
          _Fact('Identificador', person.id, selectable: true),
        ],
      );

  Widget _physical(PhysicalAttributes physical) => _SectionCard(
        icon: Icons.accessibility_new_outlined,
        eyebrow: 'II · APARÊNCIA',
        title: 'Características físicas',
        children: [
          _Fact(
              'Altura',
              physical.heightM == null
                  ? null
                  : '${_number(physical.heightM!)} m'),
          _Fact(
              'Peso',
              physical.weightKg == null
                  ? null
                  : '${_number(physical.weightKg!)} kg'),
          _Fact('Cabelo', physical.hairColor),
          _Fact('Olhos', physical.eyeColor),
          _Fact('Pele', physical.skinTone),
          _Fact('Constituição', physical.bodyType),
          _Fact('Marcas distintivas', physical.distinctiveFeatures),
          _LongText('Descrição', physical.description),
          _CustomAttributes(physical.customAttributes),
        ],
      );

  Widget _personality(PersonalityProfile personality) => _SectionCard(
        icon: Icons.psychology_outlined,
        eyebrow: 'III · ESSÊNCIA',
        title: 'Personalidade',
        children: [
          _TagGroup('Características', personality.traits),
          _TagGroup('Virtudes', personality.virtues),
          _TagGroup('Defeitos', personality.flaws),
          _TagGroup('Ambições', personality.ambitions),
          _TagGroup('Medos', personality.fears),
          _TagGroup('Desejos', personality.desires),
          _LongText('Descrição', personality.description),
          _CustomAttributes(personality.customAttributes),
        ],
      );

  Widget _social(SocialProfile social) => _SectionCard(
        icon: Icons.account_balance_outlined,
        eyebrow: 'IV · SOCIEDADE',
        title: 'Vida social',
        children: [
          _Fact('Título', social.title),
          _Fact('Ocupação', social.occupation),
          _Fact('Residência', social.residence),
          _Fact('Nacionalidade', social.nationality),
          _Fact('Religião', social.religion),
          _Fact('Condição social', social.socialStatus),
          _LongText('Descrição', social.description),
          _CustomAttributes(social.customAttributes),
        ],
      );

  Widget _history(CharacterHistory history, String? legacyBiography) {
    final biography = history.biography ?? legacyBiography;
    final events = history.chronologicalEvents;
    return _SectionCard(
      icon: Icons.auto_stories_outlined,
      eyebrow: 'V · MEMÓRIA',
      title: 'História e acontecimentos',
      children: [
        _LongText('Biografia', biography),
        const Padding(
          padding: EdgeInsets.only(top: 7, bottom: 10),
          child: Text('LINHA DO TEMPO', style: _eyebrowStyle),
        ),
        if (events.isEmpty)
          const Text('Nenhum acontecimento registrado.',
              style:
                  TextStyle(color: ArconteColors.secondaryText, fontSize: 13))
        else
          for (final event in events) _EventTile(event: event),
        _CustomAttributes(history.customAttributes),
      ],
    );
  }
}

class _CharacterHero extends StatelessWidget {
  const _CharacterHero({required this.character, required this.onRefresh});

  final Character character;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) {
    final title = character.title?.trim().isNotEmpty == true
        ? character.title!
        : 'Personagem do códice';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 25, vertical: 27),
      decoration: BoxDecoration(
        color: ArconteColors.forest,
        border: Border.all(color: ArconteColors.brass.withValues(alpha: .65)),
        borderRadius: BorderRadius.circular(17),
      ),
      child: LayoutBuilder(builder: (context, constraints) {
        final compact = constraints.maxWidth < 450;
        final portrait = Container(
          width: compact ? 55 : 77,
          height: compact ? 63 : 86,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: ArconteColors.forestLight,
            borderRadius: BorderRadius.circular(12),
            border:
                Border.all(color: ArconteColors.paleGold.withValues(alpha: .6)),
          ),
          child: Icon(Icons.person_outline,
              size: compact ? 30 : 40, color: ArconteColors.paleGold),
        );
        final info = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SmallCaps('REGISTRO INDIVIDUAL',
                color: ArconteColors.paleGold),
            const SizedBox(height: 10),
            Text(character.fullName,
                softWrap: true,
                style: ArconteType.heading.copyWith(
                  color: ArconteColors.white,
                  fontSize: compact ? 26 : 32,
                )),
            const SizedBox(height: 8),
            Text(title,
                style: const TextStyle(
                    color: ArconteColors.paleGold, fontSize: 13)),
          ],
        );
        if (compact) {
          return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                portrait,
                const SizedBox(height: 18),
                info,
                const SizedBox(height: 14),
                TextButton.icon(
                  onPressed: onRefresh,
                  icon: const Icon(Icons.refresh, size: 17),
                  label: const Text('Atualizar ficha'),
                  style: TextButton.styleFrom(
                      foregroundColor: ArconteColors.paleGold),
                ),
              ]);
        }
        return Row(children: [
          portrait,
          const SizedBox(width: 22),
          Expanded(child: info),
          IconButton(
            tooltip: 'Atualizar ficha',
            onPressed: onRefresh,
            icon: const Icon(Icons.refresh, color: ArconteColors.paleGold),
          ),
        ]);
      }),
    );
  }
}

const _eyebrowStyle = TextStyle(
  color: ArconteColors.forestLight,
  fontSize: 10,
  fontWeight: FontWeight.w800,
  letterSpacing: 1.5,
);

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.icon,
    required this.eyebrow,
    required this.title,
    required this.children,
  });

  final IconData icon;
  final String eyebrow;
  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(23),
      decoration: BoxDecoration(
        color: ArconteColors.paper,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ArconteColors.border),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(icon, size: 22, color: ArconteColors.brass),
          const SizedBox(width: 10),
          Expanded(child: Text(eyebrow, style: _eyebrowStyle)),
        ]),
        const SizedBox(height: 11),
        Text(title, style: ArconteType.cardTitle),
        const SizedBox(height: 16),
        Container(height: 1, color: ArconteColors.border),
        const SizedBox(height: 18),
        ...children,
      ]),
    );
  }
}

class _Fact extends StatelessWidget {
  const _Fact(this.label, this.value, {this.selectable = false});

  final String label;
  final String? value;
  final bool selectable;

  @override
  Widget build(BuildContext context) {
    final shown = value?.trim().isNotEmpty == true ? value! : 'Não informado';
    return Padding(
      padding: const EdgeInsets.only(bottom: 13),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label.toUpperCase(), style: _eyebrowStyle),
        const SizedBox(height: 4),
        if (selectable)
          SelectableText(shown,
              style: const TextStyle(
                  fontSize: 13.5, color: ArconteColors.text, height: 1.45))
        else
          Text(shown,
              style: TextStyle(
                  fontSize: 13.5,
                  height: 1.45,
                  color: value?.trim().isNotEmpty == true
                      ? ArconteColors.text
                      : ArconteColors.secondaryText)),
      ]),
    );
  }
}

class _LongText extends StatelessWidget {
  const _LongText(this.label, this.content);

  final String label;
  final String? content;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label.toUpperCase(), style: _eyebrowStyle),
        const SizedBox(height: 7),
        SelectableText(
          content?.trim().isNotEmpty == true ? content! : 'Não informado',
          style: TextStyle(
              color: content?.trim().isNotEmpty == true
                  ? ArconteColors.text
                  : ArconteColors.secondaryText,
              fontSize: 13.5,
              height: 1.65),
        ),
      ]),
    );
  }
}

class _TagGroup extends StatelessWidget {
  const _TagGroup(this.label, this.values);

  final String label;
  final List<String> values;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 17),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label.toUpperCase(), style: _eyebrowStyle),
        const SizedBox(height: 8),
        if (values.isEmpty)
          const Text('Não informado',
              style:
                  TextStyle(color: ArconteColors.secondaryText, fontSize: 13))
        else
          Wrap(spacing: 7, runSpacing: 7, children: [
            for (final item in values)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
                decoration: BoxDecoration(
                  color: ArconteColors.softPaper,
                  border: Border.all(color: ArconteColors.border),
                  borderRadius: BorderRadius.circular(7),
                ),
                child: Text(item,
                    style: const TextStyle(
                        fontSize: 12, color: ArconteColors.forest)),
              ),
          ]),
      ]),
    );
  }
}

class _EventTile extends StatelessWidget {
  const _EventTile({required this.event});

  final HistoryEvent event;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 13),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Container(
          width: 6,
          height: 6,
          margin: const EdgeInsets.only(top: 9),
          decoration: const BoxDecoration(
              color: ArconteColors.brass, shape: BoxShape.circle),
        ),
        const SizedBox(width: 12),
        Expanded(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${event.year?.toString() ?? 'Sem data'}  ·  ${event.title}',
              style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 13.5,
                  color: ArconteColors.ink)),
          if (event.category?.trim().isNotEmpty == true) ...[
            const SizedBox(height: 3),
            Text(event.category!,
                style: const TextStyle(
                    fontSize: 11, color: ArconteColors.forestLight)),
          ],
          if (event.description?.trim().isNotEmpty == true) ...[
            const SizedBox(height: 5),
            SelectableText(event.description!,
                style: const TextStyle(
                    fontSize: 13,
                    height: 1.5,
                    color: ArconteColors.secondaryText)),
          ],
        ])),
      ]),
    );
  }
}

class _CustomAttributes extends StatelessWidget {
  const _CustomAttributes(this.attributes);

  final Map<String, dynamic> attributes;

  @override
  Widget build(BuildContext context) {
    if (attributes.isEmpty) return const SizedBox.shrink();
    final pretty = const JsonEncoder.withIndent('  ').convert(attributes);
    return ExpansionTile(
      tilePadding: EdgeInsets.zero,
      childrenPadding: EdgeInsets.zero,
      iconColor: ArconteColors.forest,
      title: Text('Atributos personalizados',
          style: ArconteType.cardTitle.copyWith(fontSize: 16)),
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(13),
          decoration: BoxDecoration(
            color: ArconteColors.softPaper,
            borderRadius: BorderRadius.circular(8),
          ),
          child: SelectableText(pretty,
              style: const TextStyle(
                  color: ArconteColors.text,
                  fontFamily: 'monospace',
                  fontSize: 11.5,
                  height: 1.45)),
        ),
      ],
    );
  }
}

class _StatusCard extends StatelessWidget {
  const _StatusCard({
    required this.title,
    required this.description,
    this.loading = false,
    this.onRetry,
  });

  final String title;
  final String description;
  final bool loading;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 24),
      padding: const EdgeInsets.symmetric(horizontal: 25, vertical: 45),
      decoration: BoxDecoration(
        color: ArconteColors.paper,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ArconteColors.border),
      ),
      child: Column(children: [
        if (loading)
          const CircularProgressIndicator(color: ArconteColors.forest)
        else
          const Icon(Icons.error_outline,
              color: ArconteColors.crimson, size: 39),
        const SizedBox(height: 18),
        Text(title, style: ArconteType.cardTitle, textAlign: TextAlign.center),
        const SizedBox(height: 9),
        Text(description,
            textAlign: TextAlign.center,
            style: const TextStyle(
                fontSize: 13, color: ArconteColors.secondaryText)),
        if (onRetry != null) ...[
          const SizedBox(height: 18),
          FilledButton.tonal(
              onPressed: onRetry, child: const Text('Tentar novamente')),
        ],
      ]),
    );
  }
}

String? _year(int? value) => value?.toString();

String _number(double value) {
  if (value == value.roundToDouble()) return value.toStringAsFixed(0);
  return value
      .toStringAsFixed(2)
      .replaceFirst(RegExp(r'0+$'), '')
      .replaceFirst(RegExp(r'\.$'), '')
      .replaceAll('.', ',');
}
