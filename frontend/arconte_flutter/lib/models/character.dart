/// Modelos de leitura para a API de personagens do Arconte.
///
/// Compatível com:
///   GET /api/characters        (resumos)
///   GET /api/characters/{uuid} (ficha completa)
///
/// Os campos `physical`, `personality`, `social` e `history` são nulos quando
/// o objeto veio da listagem. Um perfil vazio, porém presente na ficha
/// completa, é representado por seu objeto correspondente.
///
/// Este arquivo não depende de Flutter nem de bibliotecas externas.

class Character {
  const Character({
    required this.id,
    required this.name,
    required this.fullName,
    this.surname,
    this.gender,
    this.birthYear,
    this.deathYear,
    this.title,
    this.biography,
    this.physical,
    this.personality,
    this.social,
    this.history,
  });

  final String id;
  final String name;
  final String fullName;
  final String? surname;
  final String? gender;
  final int? birthYear;
  final int? deathYear;
  final String? title;

  /// Disponível somente em GET /api/characters/{id}.
  final String? biography;
  final PhysicalAttributes? physical;
  final PersonalityProfile? personality;
  final SocialProfile? social;
  final CharacterHistory? history;

  /// Distingue a ficha completa de um resumo de listagem.
  bool get hasDetails =>
      physical != null &&
      personality != null &&
      social != null &&
      history != null;

  bool get isDeceased => deathYear != null;

  /// Interpreta tanto o resumo quanto a ficha completa da API FastAPI.
  factory Character.fromJson(Map<String, dynamic> json) {
    return Character(
      id: _requiredString(json, 'id', 'personagem'),
      name: _requiredString(json, 'name', 'personagem'),
      fullName: _requiredString(json, 'full_name', 'personagem'),
      surname: _optionalString(json, 'surname', 'personagem'),
      gender: _optionalString(json, 'gender', 'personagem'),
      birthYear: _optionalInt(json, 'birth_year', 'personagem'),
      deathYear: _optionalInt(json, 'death_year', 'personagem'),
      title: _optionalString(json, 'title', 'personagem'),
      biography: _optionalString(json, 'biography', 'personagem'),
      physical: _optionalObject(json, 'physical', 'personagem') == null
          ? null
          : PhysicalAttributes.fromJson(
              _requiredObject(json, 'physical', 'personagem')),
      personality: _optionalObject(json, 'personality', 'personagem') == null
          ? null
          : PersonalityProfile.fromJson(
              _requiredObject(json, 'personality', 'personagem')),
      social: _optionalObject(json, 'social', 'personagem') == null
          ? null
          : SocialProfile.fromJson(
              _requiredObject(json, 'social', 'personagem')),
      history: _optionalObject(json, 'history', 'personagem') == null
          ? null
          : CharacterHistory.fromJson(
              _requiredObject(json, 'history', 'personagem')),
    );
  }

  @override
  String toString() => fullName;
}

class PhysicalAttributes {
  const PhysicalAttributes({
    this.heightM,
    this.weightKg,
    this.hairColor,
    this.eyeColor,
    this.skinTone,
    this.bodyType,
    this.distinctiveFeatures,
    this.description,
    this.customAttributes = const {},
  });

  final double? heightM;
  final double? weightKg;
  final String? hairColor;
  final String? eyeColor;
  final String? skinTone;
  final String? bodyType;
  final String? distinctiveFeatures;
  final String? description;
  final Map<String, dynamic> customAttributes;

  factory PhysicalAttributes.fromJson(Map<String, dynamic> json) {
    const where = 'physical';
    return PhysicalAttributes(
      heightM: _optionalDouble(json, 'height_m', where),
      weightKg: _optionalDouble(json, 'weight_kg', where),
      hairColor: _optionalString(json, 'hair_color', where),
      eyeColor: _optionalString(json, 'eye_color', where),
      skinTone: _optionalString(json, 'skin_tone', where),
      bodyType: _optionalString(json, 'body_type', where),
      distinctiveFeatures: _optionalString(json, 'distinctive_features', where),
      description: _optionalString(json, 'description', where),
      customAttributes: _attributes(json, where),
    );
  }
}

class PersonalityProfile {
  const PersonalityProfile({
    this.traits = const [],
    this.virtues = const [],
    this.flaws = const [],
    this.ambitions = const [],
    this.fears = const [],
    this.desires = const [],
    this.description,
    this.customAttributes = const {},
  });

  final List<String> traits;
  final List<String> virtues;
  final List<String> flaws;
  final List<String> ambitions;
  final List<String> fears;
  final List<String> desires;
  final String? description;
  final Map<String, dynamic> customAttributes;

  factory PersonalityProfile.fromJson(Map<String, dynamic> json) {
    const where = 'personality';
    return PersonalityProfile(
      traits: _stringList(json, 'traits', where),
      virtues: _stringList(json, 'virtues', where),
      flaws: _stringList(json, 'flaws', where),
      ambitions: _stringList(json, 'ambitions', where),
      fears: _stringList(json, 'fears', where),
      desires: _stringList(json, 'desires', where),
      description: _optionalString(json, 'description', where),
      customAttributes: _attributes(json, where),
    );
  }
}

class SocialProfile {
  const SocialProfile({
    this.title,
    this.occupation,
    this.residence,
    this.nationality,
    this.religion,
    this.socialStatus,
    this.description,
    this.customAttributes = const {},
  });

  final String? title;
  final String? occupation;
  final String? residence;
  final String? nationality;
  final String? religion;
  final String? socialStatus;
  final String? description;
  final Map<String, dynamic> customAttributes;

  factory SocialProfile.fromJson(Map<String, dynamic> json) {
    const where = 'social';
    return SocialProfile(
      title: _optionalString(json, 'title', where),
      occupation: _optionalString(json, 'occupation', where),
      residence: _optionalString(json, 'residence', where),
      nationality: _optionalString(json, 'nationality', where),
      religion: _optionalString(json, 'religion', where),
      socialStatus: _optionalString(json, 'social_status', where),
      description: _optionalString(json, 'description', where),
      customAttributes: _attributes(json, where),
    );
  }
}

class HistoryEvent {
  const HistoryEvent({
    required this.id,
    required this.title,
    this.year,
    this.category,
    this.description,
  });

  final String id;
  final String title;
  final int? year;
  final String? category;
  final String? description;

  factory HistoryEvent.fromJson(Map<String, dynamic> json) {
    const where = 'history.events';
    return HistoryEvent(
      id: _requiredString(json, 'id', where),
      title: _requiredString(json, 'title', where),
      year: _optionalInt(json, 'year', where),
      category: _optionalString(json, 'category', where),
      description: _optionalString(json, 'description', where),
    );
  }
}

class CharacterHistory {
  const CharacterHistory({
    this.biography,
    this.events = const [],
    this.customAttributes = const {},
  });

  final String? biography;
  final List<HistoryEvent> events;
  final Map<String, dynamic> customAttributes;

  /// Ordena por ano. Eventos sem data ficam por último; não altera [events].
  List<HistoryEvent> get chronologicalEvents {
    final indexed = events.asMap().entries.toList();
    indexed.sort((a, b) {
      final yearA = a.value.year;
      final yearB = b.value.year;
      if (yearA == null && yearB == null) return a.key.compareTo(b.key);
      if (yearA == null) return 1;
      if (yearB == null) return -1;
      final result = yearA.compareTo(yearB);
      return result != 0 ? result : a.key.compareTo(b.key);
    });
    return List<HistoryEvent>.unmodifiable(
      indexed.map((entry) => entry.value),
    );
  }

  factory CharacterHistory.fromJson(Map<String, dynamic> json) {
    const where = 'history';
    final rawEvents = json['events'];
    if (rawEvents != null && rawEvents is! List) {
      throw const FormatException('history.events deve ser uma lista.');
    }
    final events = <HistoryEvent>[];
    for (final raw in (rawEvents as List? ?? const [])) {
      if (raw is! Map<String, dynamic>) {
        throw const FormatException(
            'history.events contém um evento inválido.');
      }
      events.add(HistoryEvent.fromJson(raw));
    }
    return CharacterHistory(
      biography: _optionalString(json, 'biography', where),
      events: List<HistoryEvent>.unmodifiable(events),
      customAttributes: _attributes(json, where),
    );
  }
}

// ---- Validação da resposta HTTP (mantida privada ao modelo) -----------------

String _requiredString(Map<String, dynamic> json, String field, String where) {
  final value = json[field];
  if (value is! String || value.trim().isEmpty) {
    throw FormatException('$where.$field deve ser um texto não vazio.');
  }
  return value;
}

String? _optionalString(Map<String, dynamic> json, String field, String where) {
  final value = json[field];
  if (value == null) return null;
  if (value is! String) {
    throw FormatException('$where.$field deve ser um texto ou null.');
  }
  return value;
}

int? _optionalInt(Map<String, dynamic> json, String field, String where) {
  final value = json[field];
  if (value == null) return null;
  if (value is! int) {
    throw FormatException('$where.$field deve ser um inteiro ou null.');
  }
  return value;
}

double? _optionalDouble(Map<String, dynamic> json, String field, String where) {
  final value = json[field];
  if (value == null) return null;
  if (value is! num || !value.isFinite) {
    throw FormatException('$where.$field deve ser um número finito ou null.');
  }
  return value.toDouble();
}

Map<String, dynamic>? _optionalObject(
  Map<String, dynamic> json,
  String field,
  String where,
) {
  if (!json.containsKey(field)) return null;
  final value = json[field];
  if (value is! Map<String, dynamic>) {
    throw FormatException('$where.$field deve ser um objeto JSON.');
  }
  return value;
}

Map<String, dynamic> _requiredObject(
  Map<String, dynamic> json,
  String field,
  String where,
) {
  return _optionalObject(json, field, where) ??
      (throw FormatException('$where.$field está ausente.'));
}

List<String> _stringList(
  Map<String, dynamic> json,
  String field,
  String where,
) {
  final value = json[field];
  if (value == null) return const [];
  if (value is! List || value.any((element) => element is! String)) {
    throw FormatException('$where.$field deve ser uma lista de textos.');
  }
  return List<String>.unmodifiable(value.cast<String>());
}

Map<String, dynamic> _attributes(Map<String, dynamic> json, String where) {
  final value = json['custom_attributes'];
  if (value == null) return const {};
  if (value is! Map<String, dynamic>) {
    throw FormatException('$where.custom_attributes deve ser um objeto JSON.');
  }
  return Map<String, dynamic>.unmodifiable(value);
}
