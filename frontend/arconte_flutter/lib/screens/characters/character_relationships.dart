import 'package:flutter/material.dart';

import '../../models/character.dart';
import '../../services/character_api.dart';
import '../../services/relationship_api.dart';
import '../../theme/arconte_theme.dart';
import '../../widgets/ornaments.dart';

/// Vínculos familiares de um personagem já cadastrado.
///
/// Este componente é independente da ficha: não cria Scaffold nem rolagem
/// própria. Pode ser colocado no SingleChildScrollView do WorkspaceScreen.
///
/// A criação e a exclusão são delegadas ao FastAPI, que mantém as regras de
/// genealogia, verifica ciclos e duplicidades e salva o projeto JSON.
///
/// [relationshipApi] e [characterApi] podem ser injetados para testes. Quando
/// não forem fornecidos, serão criados e descartados pelo componente.
/// [onChanged] é chamado após uma criação ou exclusão bem-sucedida.
class CharacterRelationships extends StatefulWidget {
  const CharacterRelationships({
    super.key,
    required this.characterId,
    this.characterName,
    this.relationshipApi,
    this.characterApi,
    this.onChanged,
  });

  final String characterId;
  final String? characterName;
  final RelationshipApi? relationshipApi;
  final CharacterApi? characterApi;
  final VoidCallback? onChanged;

  @override
  State<CharacterRelationships> createState() => _CharacterRelationshipsState();
}

/// Escolhas expressas da perspectiva do personagem cuja ficha está aberta.
/// Para filiação, o FastAPI sempre espera responsável -> filho(a).
enum _RelationshipChoice {
  biologicalParent,
  adoptiveParent,
  biologicalChild,
  adoptiveChild,
  marriage,
  partnership,
}

extension _RelationshipChoiceInfo on _RelationshipChoice {
  String get label {
    switch (this) {
      case _RelationshipChoice.biologicalParent:
        return 'Pai/mãe biológico(a)';
      case _RelationshipChoice.adoptiveParent:
        return 'Pai/mãe adotivo(a)';
      case _RelationshipChoice.biologicalChild:
        return 'Filho(a) biológico(a)';
      case _RelationshipChoice.adoptiveChild:
        return 'Filho(a) adotivo(a)';
      case _RelationshipChoice.marriage:
        return 'Casamento';
      case _RelationshipChoice.partnership:
        return 'União';
    }
  }

  String get apiType {
    switch (this) {
      case _RelationshipChoice.biologicalParent:
      case _RelationshipChoice.biologicalChild:
        return 'biological_parent';
      case _RelationshipChoice.adoptiveParent:
      case _RelationshipChoice.adoptiveChild:
        return 'adoptive_parent';
      case _RelationshipChoice.marriage:
        return 'marriage';
      case _RelationshipChoice.partnership:
        return 'partnership';
    }
  }

  bool get selectedPersonIsParent =>
      this == _RelationshipChoice.biologicalParent ||
      this == _RelationshipChoice.adoptiveParent;
}

class _CharacterRelationshipsState extends State<CharacterRelationships> {
  final _formKey = GlobalKey<FormState>();
  final _startYear = TextEditingController();
  final _endYear = TextEditingController();

  late final RelationshipApi _relationshipApi;
  late final CharacterApi _characterApi;
  late final bool _ownsRelationshipApi;
  late final bool _ownsCharacterApi;

  List<RelationshipRecord> _relationships = const [];
  List<Character> _candidates = const [];
  bool _loading = true;
  bool _loadingCandidates = false;
  bool _adding = false;
  bool _working = false;
  String? _loadError;
  String? _actionError;
  String? _otherCharacterId;
  _RelationshipChoice _choice = _RelationshipChoice.biologicalParent;
  int _loadGeneration = 0;
  int _candidateGeneration = 0;

  @override
  void initState() {
    super.initState();
    _ownsRelationshipApi = widget.relationshipApi == null;
    _ownsCharacterApi = widget.characterApi == null;
    _relationshipApi = widget.relationshipApi ?? RelationshipApi();
    _characterApi = widget.characterApi ?? CharacterApi();
    _loadRelationships();
  }

  @override
  void didUpdateWidget(covariant CharacterRelationships oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.characterId != widget.characterId) {
      // Descarta resultados de requisições anteriores ao trocar de ficha.
      _candidateGeneration++;
      _adding = false;
      _working = false;
      _loadingCandidates = false;
      _otherCharacterId = null;
      _actionError = null;
      _candidates = const [];
      _startYear.clear();
      _endYear.clear();
      _choice = _RelationshipChoice.biologicalParent;
      _loadRelationships();
    }
  }

  @override
  void dispose() {
    _loadGeneration++;
    _candidateGeneration++;
    _startYear.dispose();
    _endYear.dispose();
    if (_ownsRelationshipApi) _relationshipApi.dispose();
    if (_ownsCharacterApi) _characterApi.dispose();
    super.dispose();
  }

  Future<void> _loadRelationships({bool showLoading = true}) async {
    final generation = ++_loadGeneration;
    final characterId = widget.characterId;
    if (showLoading) {
      setState(() {
        _loading = true;
        _loadError = null;
        _relationships = const [];
      });
    }
    try {
      final records = await _relationshipApi.getRelationships(characterId);
      if (!mounted || generation != _loadGeneration ||
          characterId != widget.characterId) {
        return;
      }
      setState(() {
        _relationships = records;
        _loading = false;
        _loadError = null;
      });
    } catch (error) {
      if (!mounted || generation != _loadGeneration ||
          characterId != widget.characterId) {
        return;
      }
      setState(() {
        _loading = false;
        _loadError = _readableError(error);
      });
    }
  }

  Future<void> _beginAdd() async {
    if (_working || _loadingCandidates) return;
    final generation = ++_candidateGeneration;
    final characterId = widget.characterId;
    setState(() {
      _loadingCandidates = true;
      _actionError = null;
    });
    try {
      final people = await _characterApi.getCharacters();
      if (!mounted || generation != _candidateGeneration ||
          characterId != widget.characterId) {
        return;
      }
      final others = people.where((person) => person.id != characterId).toList()
        ..sort((a, b) => a.fullName.toLowerCase()
            .compareTo(b.fullName.toLowerCase()));
      setState(() {
        _candidates = others;
        _choice = _RelationshipChoice.biologicalParent;
        _otherCharacterId = null;
        _startYear.clear();
        _endYear.clear();
        _adding = true;
      });
    } catch (error) {
      if (!mounted || generation != _candidateGeneration ||
          characterId != widget.characterId) {
        return;
      }
      setState(() => _actionError = _readableError(error));
    } finally {
      if (mounted && generation == _candidateGeneration &&
          characterId == widget.characterId) {
        setState(() => _loadingCandidates = false);
      }
    }
  }

  void _cancelAdd() {
    if (_working) return;
    setState(() {
      _adding = false;
      _actionError = null;
      _otherCharacterId = null;
    });
  }

  Future<void> _create() async {
    if (_working || !_formKey.currentState!.validate()) return;
    final otherId = _otherCharacterId;
    if (otherId == null) return;

    final currentId = widget.characterId;
    final selectedIsParent = _choice.selectedPersonIsParent;
    final payload = <String, dynamic>{
      'source_id': selectedIsParent ? otherId : currentId,
      'target_id': selectedIsParent ? currentId : otherId,
      'type': _choice.apiType,
      'start_year': _parseYear(_startYear.text),
      'end_year': _parseYear(_endYear.text),
    };
    setState(() {
      _working = true;
      _actionError = null;
    });
    try {
      await _relationshipApi.createRelationship(payload);
      if (!mounted || currentId != widget.characterId) return;
      setState(() => _adding = false);
      await _loadRelationships(showLoading: false);
      if (!mounted || currentId != widget.characterId) return;
      widget.onChanged?.call();
      _notify('Vínculo familiar registrado.');
    } catch (error) {
      if (!mounted || currentId != widget.characterId) return;
      setState(() => _actionError = _readableError(error));
    } finally {
      if (mounted && currentId == widget.characterId) {
        setState(() => _working = false);
      }
    }
  }

  Future<void> _delete(RelationshipRecord relation) async {
    if (_working) return;
    final currentId = widget.characterId;
    final otherName = _otherName(relation);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remover vínculo familiar?'),
        content: Text(
          'O vínculo com $otherName será removido da genealogia. '
          'Os personagens e seus demais relacionamentos serão preservados.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: FilledButton.styleFrom(backgroundColor: ArconteColors.crimson),
            child: const Text('Remover vínculo'),
          ),
        ],
      ),
    );
    if (!mounted || confirmed != true || _working ||
        currentId != widget.characterId) {
      return;
    }

    setState(() {
      _working = true;
      _actionError = null;
    });
    try {
      await _relationshipApi.deleteRelationship(relation.id);
      if (!mounted || currentId != widget.characterId) return;
      await _loadRelationships(showLoading: false);
      if (!mounted || currentId != widget.characterId) return;
      widget.onChanged?.call();
      _notify('Vínculo familiar removido.');
    } catch (error) {
      if (!mounted || currentId != widget.characterId) return;
      setState(() => _actionError = _readableError(error));
    } finally {
      if (mounted && currentId == widget.characterId) {
        setState(() => _working = false);
      }
    }
  }

  void _notify(String message) {
    ScaffoldMessenger.maybeOf(context)?.showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  String _otherName(RelationshipRecord relation) {
    return relation.sourceId == widget.characterId
        ? relation.targetName
        : relation.sourceName;
  }

  static int? _parseYear(String text) {
    final value = text.trim();
    return value.isEmpty ? null : int.parse(value);
  }

  static String _readableError(Object error) {
    if (error is RelationshipApiException) return error.message;
    if (error is CharacterApiException) return error.message;
    return 'Não foi possível concluir a operação. Verifique a conexão com o Arconte.';
  }

  @override
  Widget build(BuildContext context) {
    final parents = <RelationshipRecord>[];
    final children = <RelationshipRecord>[];
    final partners = <RelationshipRecord>[];
    for (final relation in _relationships) {
      if (!relation.isDirected) {
        partners.add(relation);
      } else if (relation.targetId == widget.characterId) {
        parents.add(relation);
      } else if (relation.sourceId == widget.characterId) {
        children.add(relation);
      }
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(23),
      decoration: BoxDecoration(
        color: ArconteColors.paper,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ArconteColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LayoutBuilder(builder: (context, constraints) {
            final compact = constraints.maxWidth < 520;
            final heading = const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'VI · LINHAGENS E LAÇOS',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    color: ArconteColors.forestLight,
                    letterSpacing: 1.5,
                  ),
                ),
                SizedBox(height: 9),
                Text('Vínculos familiares', style: ArconteType.cardTitle),
                SizedBox(height: 5),
                Text(
                  'Pais, filhos, casamentos e uniões registrados no códice.',
                  style: TextStyle(
                    fontSize: 12.5,
                    color: ArconteColors.secondaryText,
                    height: 1.4,
                  ),
                ),
              ],
            );
            final addButton = FilledButton.icon(
              key: const Key('add-relationship-button'),
              onPressed: _working || _loadingCandidates || _adding
                  ? null
                  : _beginAdd,
              icon: _loadingCandidates
                  ? const SizedBox(
                      width: 17,
                      height: 17,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: ArconteColors.paleGold,
                      ),
                    )
                  : const Icon(Icons.add_link, size: 18),
              label: const Text('Adicionar vínculo'),
              style: FilledButton.styleFrom(
                backgroundColor: ArconteColors.forest,
                foregroundColor: ArconteColors.paleGold,
                padding: const EdgeInsets.symmetric(horizontal: 17, vertical: 15),
              ),
            );
            return compact
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      heading,
                      const SizedBox(height: 15),
                      addButton,
                    ],
                  )
                : Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Expanded(child: heading),
                      const SizedBox(width: 14),
                      addButton,
                    ],
                  );
          }),
          const SizedBox(height: 20),
          const DecorativeRule(width: 70),
          if (_actionError != null) ...[
            const SizedBox(height: 15),
            _Message(text: _actionError!, error: true),
          ],
          if (_adding) ...[
            const SizedBox(height: 20),
            _buildCreationForm(),
          ],
          const SizedBox(height: 19),
          if (_loading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 28),
              child: Center(
                child: CircularProgressIndicator(color: ArconteColors.forest),
              ),
            )
          else if (_loadError != null) ...[
            _Message(text: _loadError!, error: true),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _working ? null : () => _loadRelationships(),
              icon: const Icon(Icons.refresh, size: 18),
              label: const Text('Tentar novamente'),
            ),
          ] else ...[
            if (_relationships.isEmpty)
              const _Message(
                text: 'Nenhum vínculo familiar registrado. '
                    'Adicione um personagem existente para começar.',
              )
            else ...[
              _buildGroup(
                title: 'Pais e responsáveis',
                icon: Icons.family_restroom_outlined,
                records: parents,
              ),
              const SizedBox(height: 18),
              _buildGroup(
                title: 'Filhos',
                icon: Icons.people_outline,
                records: children,
              ),
              const SizedBox(height: 18),
              _buildGroup(
                title: 'Casamentos e uniões',
                icon: Icons.favorite_border,
                records: partners,
              ),
            ],
            const SizedBox(height: 11),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: _working ? null : () => _loadRelationships(),
                icon: const Icon(Icons.refresh, size: 16),
                label: const Text('Atualizar vínculos'),
                style: TextButton.styleFrom(
                  foregroundColor: ArconteColors.forestLight,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildGroup({
    required String title,
    required IconData icon,
    required List<RelationshipRecord> records,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: ArconteColors.brass, size: 19),
            const SizedBox(width: 9),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 14,
                  color: ArconteColors.forest,
                ),
              ),
            ),
            Text(
              '${records.length}',
              style: const TextStyle(color: ArconteColors.secondaryText),
            ),
          ],
        ),
        const SizedBox(height: 9),
        if (records.isEmpty)
          const Padding(
            padding: EdgeInsets.only(left: 28, bottom: 3),
            child: Text(
              'Nenhum vínculo registrado.',
              style: TextStyle(
                fontSize: 12.5,
                color: ArconteColors.secondaryText,
              ),
            ),
          )
        else
          for (final relation in records) ...[
            _buildRelationTile(relation),
            const SizedBox(height: 7),
          ],
      ],
    );
  }

  Widget _buildRelationTile(RelationshipRecord relation) {
    final description = switch (relation.type) {
      'biological_parent' => 'Filiação biológica',
      'adoptive_parent' => 'Filiação adotiva',
      'marriage' => 'Casamento',
      'partnership' => 'União',
      _ => 'Vínculo familiar',
    };
    final period = _period(relation.startYear, relation.endYear);
    return Container(
      decoration: BoxDecoration(
        color: ArconteColors.softPaper,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: ArconteColors.border),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9),
      child: Row(
        children: [
          const Icon(Icons.person_outline, size: 21, color: ArconteColors.forestLight),
          const SizedBox(width: 11),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _otherName(relation),
                  style: const TextStyle(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                    color: ArconteColors.text,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  period == null ? description : '$description · $period',
                  style: const TextStyle(
                    fontSize: 11.5,
                    color: ArconteColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            key: ValueKey('delete-relationship-${relation.id}'),
            onPressed: _working ? null : () => _delete(relation),
            tooltip: 'Remover vínculo com ${_otherName(relation)}',
            icon: const Icon(Icons.link_off, color: ArconteColors.crimson, size: 20),
          ),
        ],
      ),
    );
  }

  static String? _period(int? start, int? end) {
    if (start != null && end != null) return '$start–$end';
    if (start != null) return 'desde $start';
    if (end != null) return 'até $end';
    return null;
  }

  Widget _buildCreationForm() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: ArconteColors.softPaper,
        borderRadius: BorderRadius.circular(13),
        border: Border.all(color: ArconteColors.brass.withValues(alpha: .6)),
      ),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Novo vínculo familiar', style: ArconteType.cardTitle),
            const SizedBox(height: 7),
            Text(
              'Escolha como a outra pessoa se relaciona com '
              '${widget.characterName ?? 'este personagem'}.',
              style: const TextStyle(
                color: ArconteColors.secondaryText,
                fontSize: 12.5,
              ),
            ),
            const SizedBox(height: 17),
            DropdownButtonFormField<_RelationshipChoice>(
              key: const Key('relationship-type-field'),
              initialValue: _choice,
              isExpanded: true,
              decoration: const InputDecoration(labelText: 'Tipo de vínculo'),
              items: _RelationshipChoice.values
                  .map(
                    (choice) => DropdownMenuItem(
                      value: choice,
                      child: Text(choice.label),
                    ),
                  )
                  .toList(),
              onChanged: _working
                  ? null
                  : (value) {
                      if (value != null) setState(() => _choice = value);
                    },
            ),
            const SizedBox(height: 15),
            if (_candidates.isEmpty)
              const _Message(
                text: 'Não há outro personagem cadastrado neste mundo. '
                    'Crie outro personagem antes de adicionar um vínculo.',
              )
            else
              Autocomplete<Character>(
                displayStringForOption: (person) => person.fullName,
                optionsBuilder: (value) {
                  final query = value.text.trim().toLowerCase();
                  return _candidates
                      .where((person) => query.isEmpty ||
                          person.fullName.toLowerCase().contains(query))
                      .take(30);
                },
                onSelected: (person) {
                  setState(() => _otherCharacterId = person.id);
                },
                fieldViewBuilder: (context, controller, focusNode, onSubmit) {
                  return TextFormField(
                    key: const Key('relationship-person-field'),
                    controller: controller,
                    focusNode: focusNode,
                    enabled: !_working,
                    decoration: const InputDecoration(
                      labelText: 'Outro personagem',
                      hintText: 'Digite o nome e selecione uma sugestão',
                      prefixIcon: Icon(Icons.person_search_outlined),
                    ),
                    onChanged: (_) {
                      if (_otherCharacterId != null) {
                        setState(() => _otherCharacterId = null);
                      }
                    },
                    validator: (_) => _otherCharacterId == null
                        ? 'Escolha um personagem da lista de sugestões.'
                        : null,
                  );
                },
              ),
            const SizedBox(height: 15),
            LayoutBuilder(builder: (context, constraints) {
              final narrow = constraints.maxWidth < 400;
              final startField = _yearField(
                controller: _startYear,
                label: 'Ano de início (opcional)',
              );
              final endField = _yearField(
                controller: _endYear,
                label: 'Ano de término (opcional)',
                checkOrder: true,
              );
              if (narrow) {
                return Column(children: [
                  startField,
                  const SizedBox(height: 12),
                  endField,
                ]);
              }
              return Row(children: [
                Expanded(child: startField),
                const SizedBox(width: 12),
                Expanded(child: endField),
              ]);
            }),
            const SizedBox(height: 16),
            Wrap(
              spacing: 11,
              runSpacing: 9,
              children: [
                FilledButton.icon(
                  key: const Key('save-relationship-button'),
                  onPressed: _working || _candidates.isEmpty ? null : _create,
                  icon: _working
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: ArconteColors.paleGold,
                          ),
                        )
                      : const Icon(Icons.check, size: 18),
                  label: Text(_working ? 'Salvando...' : 'Salvar vínculo'),
                  style: FilledButton.styleFrom(
                    backgroundColor: ArconteColors.forest,
                    foregroundColor: ArconteColors.paleGold,
                  ),
                ),
                TextButton(
                  onPressed: _working ? null : _cancelAdd,
                  child: const Text('Cancelar'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _yearField({
    required TextEditingController controller,
    required String label,
    bool checkOrder = false,
  }) {
    return TextFormField(
      controller: controller,
      enabled: !_working,
      keyboardType: const TextInputType.numberWithOptions(signed: true),
      decoration: InputDecoration(labelText: label),
      validator: (raw) {
        final value = (raw ?? '').trim();
        if (value.isNotEmpty && int.tryParse(value) == null) {
          return 'Informe um ano inteiro.';
        }
        if (checkOrder) {
          final start = int.tryParse(_startYear.text.trim());
          final end = int.tryParse(value);
          if (start != null && end != null && end < start) {
            return 'Anterior ao início.';
          }
        }
        return null;
      },
    );
  }
}

class _Message extends StatelessWidget {
  const _Message({required this.text, this.error = false});

  final String text;
  final bool error;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 12),
      decoration: BoxDecoration(
        color: error ? ArconteColors.crimson.withValues(alpha: .08) :
            ArconteColors.softPaper,
        borderRadius: BorderRadius.circular(9),
        border: Border.all(
          color: error ? ArconteColors.crimson.withValues(alpha: .4) :
              ArconteColors.border,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            error ? Icons.error_outline : Icons.info_outline,
            size: 18,
            color: error ? ArconteColors.crimson : ArconteColors.brass,
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 12.5,
                height: 1.4,
                color: error ? ArconteColors.crimson : ArconteColors.secondaryText,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
