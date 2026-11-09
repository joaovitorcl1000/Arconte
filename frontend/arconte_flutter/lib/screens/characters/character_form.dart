import 'package:flutter/material.dart';

import '../../models/character.dart';
import '../../services/character_api.dart';
import '../../theme/arconte_theme.dart';
import '../../widgets/ornaments.dart';

/// Formulário de criação/edição de personagens. Nunca salva JSON localmente:
/// POST/PATCH delegam a validação e a persistência ao backend Python.
///
/// Em edição, só envia campos alterados; eventos históricos e atributos
/// personalizados permanecem intactos. O editor de eventos será uma etapa
/// separada da interface.
class CharacterForm extends StatefulWidget {
  const CharacterForm({
    super.key,
    required this.api,
    required this.onSaved,
    required this.onCancel,
    this.initial,
  });

  final CharacterApi api;
  final Character? initial;
  final ValueChanged<Character> onSaved;
  final VoidCallback onCancel;

  @override
  State<CharacterForm> createState() => _CharacterFormState();
}

class _CharacterFormState extends State<CharacterForm> {
  final _formKey = GlobalKey<FormState>();
  final Map<String, TextEditingController> _fields = {};
  final Map<String, String> _original = {};
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _populateFields();
  }

  void _populateFields() {
    final person = widget.initial;
    final physical = person?.physical;
    final personality = person?.personality;
    final social = person?.social;
    final values = <String, String?>{
      'name': person?.name,
      'surname': person?.surname,
      'gender': person?.gender,
      'birth_year': person?.birthYear?.toString(),
      'death_year': person?.deathYear?.toString(),
      'biography': person?.history?.biography ?? person?.biography,
      'height_m': physical?.heightM?.toString(),
      'weight_kg': physical?.weightKg?.toString(),
      'hair_color': physical?.hairColor,
      'eye_color': physical?.eyeColor,
      'skin_tone': physical?.skinTone,
      'body_type': physical?.bodyType,
      'distinctive_features': physical?.distinctiveFeatures,
      'physical_description': physical?.description,
      'traits': personality?.traits.join(', '),
      'virtues': personality?.virtues.join(', '),
      'flaws': personality?.flaws.join(', '),
      'ambitions': personality?.ambitions.join(', '),
      'fears': personality?.fears.join(', '),
      'desires': personality?.desires.join(', '),
      'personality_description': personality?.description,
      'title': social?.title,
      'occupation': social?.occupation,
      'residence': social?.residence,
      'nationality': social?.nationality,
      'religion': social?.religion,
      'social_status': social?.socialStatus,
      'social_description': social?.description,
    };
    for (final item in values.entries) {
      final value = item.value ?? '';
      _original[item.key] = value;
      final controller = _fields[item.key];
      if (controller == null) {
        _fields[item.key] = TextEditingController(text: value);
      } else {
        controller.text = value;
      }
    }
  }

  @override
  void didUpdateWidget(covariant CharacterForm oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Se o mesmo widget passar a mostrar outra ficha, recarrega os campos.
    if (oldWidget.initial?.id != widget.initial?.id) {
      _populateFields();
      _error = null;
    }
  }

  @override
  void dispose() {
    for (final controller in _fields.values) {
      controller.dispose();
    }
    super.dispose();
  }

  String _value(String key) => _fields[key]!.text.trim();

  bool _changed(String key) => _value(key) != _original[key]!.trim();

  /// Só inclui campos alterados no PATCH; strings vazias limpam opcionais.
  Map<String, dynamic> _payload() {
    final edits = <String, dynamic>{};
    final identity = <String>['name', 'surname', 'gender', 'biography'];
    final years = <String>['birth_year', 'death_year'];
    for (final key in identity) {
      if (widget.initial == null || _changed(key)) {
        if (key == 'name' || _value(key).isNotEmpty || widget.initial != null) {
          edits[key] = _value(key).isEmpty ? null : _value(key);
        }
      }
    }
    for (final key in years) {
      if (widget.initial == null || _changed(key)) {
        if (_value(key).isNotEmpty || widget.initial != null) {
          edits[key] = _value(key).isEmpty ? null : int.parse(_value(key));
        }
      }
    }

    void profile(String block, Map<String, String> fields,
        {Set<String> doubles = const {}, Set<String> lists = const {}}) {
      final changed = <String, dynamic>{};
      for (final entry in fields.entries) {
        final key = entry.key;
        if (widget.initial != null && !_changed(key)) continue;
        final text = _value(key);
        if (text.isEmpty && widget.initial == null) continue;
        if (doubles.contains(key)) {
          changed[entry.value] = text.isEmpty
              ? null
              : double.parse(text.replaceAll(',', '.'));
        } else if (lists.contains(key)) {
          changed[entry.value] = text.isEmpty
              ? <String>[]
              : text.split(',').map((item) => item.trim()).where((item) => item.isNotEmpty).toList();
        } else {
          changed[entry.value] = text.isEmpty ? null : text;
        }
      }
      if (changed.isNotEmpty) edits[block] = changed;
    }

    profile('physical', {
      'height_m': 'height_m', 'weight_kg': 'weight_kg',
      'hair_color': 'hair_color', 'eye_color': 'eye_color',
      'skin_tone': 'skin_tone', 'body_type': 'body_type',
      'distinctive_features': 'distinctive_features',
      'physical_description': 'description',
    }, doubles: {'height_m', 'weight_kg'});

    profile('personality', {
      'traits': 'traits', 'virtues': 'virtues', 'flaws': 'flaws',
      'ambitions': 'ambitions', 'fears': 'fears', 'desires': 'desires',
      'personality_description': 'description',
    }, lists: {'traits', 'virtues', 'flaws', 'ambitions', 'fears', 'desires'});

    profile('social', {
      'title': 'title', 'occupation': 'occupation',
      'residence': 'residence', 'nationality': 'nationality',
      'religion': 'religion', 'social_status': 'social_status',
      'social_description': 'description',
    });
    return edits;
  }

  Future<void> _cancel() async {
    if (_saving) return;
    if (!_fields.keys.any(_changed)) {
      widget.onCancel();
      return;
    }
    final discard = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Descartar alterações?'),
        content: const Text('Os dados preenchidos ainda não foram salvos.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false),
              child: const Text('Continuar editando')),
          TextButton(onPressed: () => Navigator.pop(context, true),
              child: const Text('Descartar')),
        ],
      ),
    );
    if (mounted && discard == true) widget.onCancel();
  }

  Future<void> _save() async {
    if (_saving || !_formKey.currentState!.validate()) return;
    final birth = _value('birth_year');
    final death = _value('death_year');
    if (birth.isNotEmpty && death.isNotEmpty &&
        int.parse(death) < int.parse(birth)) {
      setState(() => _error = 'O falecimento não pode ser anterior ao nascimento.');
      return;
    }
    final changes = _payload();
    if (changes.isEmpty && widget.initial != null) {
      widget.onSaved(widget.initial!);
      return;
    }
    setState(() { _saving = true; _error = null; });
    try {
      final person = widget.initial == null
          ? await widget.api.createCharacter(changes)
          : await widget.api.updateCharacter(widget.initial!.id, changes);
      if (!mounted) return;
      widget.onSaved(person);
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = error is CharacterApiException
          ? error.message : 'Não foi possível salvar o personagem.');
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Widget _field(String key, String label,
      {int lines = 1, bool mandatory = false, bool year = false,
       bool positive = false, String? hint}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: TextFormField(
        key: ValueKey('character-field-$key'),
        controller: _fields[key],
        enabled: !_saving,
        maxLines: lines,
        keyboardType: year ? const TextInputType.numberWithOptions(signed: true)
            : positive ? const TextInputType.numberWithOptions(decimal: true)
            : lines > 1 ? TextInputType.multiline : TextInputType.text,
        decoration: InputDecoration(labelText: label, hintText: hint,
            alignLabelWithHint: lines > 1),
        validator: (text) {
          final value = (text ?? '').trim();
          if (mandatory && value.isEmpty) return 'Informe o nome do personagem.';
          if (year && value.isNotEmpty && int.tryParse(value) == null) {
            return 'Use um ano inteiro (ex.: -20, 0, 67).';
          }
          if (positive && value.isNotEmpty) {
            final number = double.tryParse(value.replaceAll(',', '.'));
            if (number == null || !number.isFinite || number <= 0) {
              return 'Informe um número positivo.';
            }
          }
          return null;
        },
      ),
    );
  }

  Widget _section(String heading, IconData icon, List<Widget> children) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 18),
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: ArconteColors.paper,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ArconteColors.border),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(icon, color: ArconteColors.brass, size: 22),
          const SizedBox(width: 12),
          Expanded(child: Text(heading, style: ArconteType.cardTitle)),
        ]),
        const SizedBox(height: 18),
        ...children,
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    final editing = widget.initial != null;
    return Form(
      key: _formKey,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        TextButton.icon(onPressed: _saving ? null : _cancel,
            icon: const Icon(Icons.arrow_back, size: 17),
            label: const Text('Voltar aos personagens')),
        const SizedBox(height: 16),
        const SmallCaps('BIBLIOTECA / PESSOAS / REGISTRO',
            color: ArconteColors.forestLight),
        const SizedBox(height: 12),
        Text(editing ? 'Editar personagem' : 'Novo personagem',
            style: ArconteType.display),
        const SizedBox(height: 12),
        const Text('Os registros serão validados e salvos pelo Arconte Python.',
            style: TextStyle(color: ArconteColors.secondaryText)),
        const SizedBox(height: 22),
        if (_error != null) ...[
          Text(_error!, style: const TextStyle(color: ArconteColors.crimson)),
          const SizedBox(height: 14),
        ],
        _section('I · Identidade', Icons.badge_outlined, [
          _field('name', 'Nome *', mandatory: true),
          _field('surname', 'Sobrenome'),
          _field('gender', 'Gênero'),
          _field('birth_year', 'Ano de nascimento', year: true),
          _field('death_year', 'Ano de falecimento', year: true),
        ]),
        _section('II · Aparência', Icons.accessibility_new_outlined, [
          _field('height_m', 'Altura (m)', positive: true),
          _field('weight_kg', 'Peso (kg)', positive: true),
          _field('hair_color', 'Cor dos cabelos'),
          _field('eye_color', 'Cor dos olhos'),
          _field('skin_tone', 'Tom de pele'),
          _field('body_type', 'Constituição'),
          _field('distinctive_features', 'Marcas distintivas'),
          _field('physical_description', 'Descrição da aparência', lines: 3),
        ]),
        _section('III · Personalidade', Icons.psychology_outlined, [
          const Text('Separe itens com vírgulas.',
              style: TextStyle(color: ArconteColors.secondaryText)),
          const SizedBox(height: 12),
          _field('traits', 'Características'),
          _field('virtues', 'Virtudes'),
          _field('flaws', 'Defeitos'),
          _field('ambitions', 'Ambições'),
          _field('fears', 'Medos'),
          _field('desires', 'Desejos'),
          _field('personality_description', 'Descrição da personalidade', lines: 3),
        ]),
        _section('IV · Vida social', Icons.account_balance_outlined, [
          _field('title', 'Título'),
          _field('occupation', 'Ocupação'),
          _field('residence', 'Residência'),
          _field('nationality', 'Nacionalidade'),
          _field('religion', 'Religião'),
          _field('social_status', 'Condição social'),
          _field('social_description', 'Descrição social', lines: 3),
        ]),
        _section('V · Memória', Icons.auto_stories_outlined, [
          _field('biography', 'Biografia', lines: 6),
          if (editing) const Text(
            'Acontecimentos e atributos personalizados já cadastrados serão preservados.',
            style: TextStyle(fontSize: 12, color: ArconteColors.secondaryText),
          ),
        ]),
        Wrap(spacing: 14, runSpacing: 12, children: [
          FilledButton.icon(
            key: const Key('character-save'),
            onPressed: _saving ? null : _save,
            icon: _saving ? const SizedBox(width: 16, height: 16,
                child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.save_outlined),
            label: Text(editing ? 'Salvar alterações' : 'Criar personagem'),
            style: FilledButton.styleFrom(
              backgroundColor: ArconteColors.forest,
              foregroundColor: ArconteColors.paleGold,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            ),
          ),
          OutlinedButton(onPressed: _saving ? null : _cancel,
              child: const Text('Cancelar')),
        ]),
        const SizedBox(height: 32),
      ]),
    );
  }
}
