/// Cliente HTTP de consulta, criação e edição dos personagens do Arconte.
///
/// O FastAPI deve estar em execução no backend:
///   cd ~/Arconte/backend/genealogy
///   python3 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
///
/// Dependência necessária no Flutter:
///   flutter pub add http
///
/// Para Flutter Web no mesmo computador, `127.0.0.1` funciona normalmente.
/// Para emulador Android use `http://10.0.2.2:8000` e configure o backend
/// para escutar em um endereço acessível ao emulador.

import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/character.dart';

class CharacterApiException implements Exception {
  const CharacterApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => statusCode == null
      ? 'CharacterApiException: $message'
      : 'CharacterApiException ($statusCode): $message';
}

class CharacterApi {
  CharacterApi({
    String baseUrl = 'http://127.0.0.1:8000',
    http.Client? client,
    this.requestTimeout = const Duration(seconds: 10),
  })  : _baseUri = _validateBaseUrl(baseUrl),
        _client = client ?? http.Client(),
        _ownsClient = client == null {
    if (requestTimeout <= Duration.zero) {
      throw ArgumentError.value(
          requestTimeout, 'requestTimeout', 'Deve ser positivo.');
    }
  }

  final Uri _baseUri;
  final http.Client _client;
  final bool _ownsClient;
  final Duration requestTimeout;

  /// GET /api/characters: devolve resumos ordenados pelo backend.
  Future<List<Character>> getCharacters() async {
    final payload = await _getJson(_endpoint());
    if (payload is! List) {
      throw const CharacterApiException(
        'A API retornou uma lista de personagens em formato inválido.',
      );
    }
    try {
      return List<Character>.unmodifiable(payload.map((item) {
        if (item is! Map<String, dynamic>) {
          throw const FormatException('Item da lista de personagens inválido.');
        }
        return Character.fromJson(item);
      }));
    } on FormatException catch (error) {
      throw CharacterApiException(
          'Dados de personagens inválidos: ${error.message}');
    } on TypeError catch (error) {
      throw CharacterApiException('Dados de personagens incompatíveis: $error');
    }
  }

  /// GET /api/characters/{id}: devolve identidade e os quatro blocos.
  Future<Character> getCharacter(String id) async {
    final normalizedId = id.trim();
    if (normalizedId.isEmpty) {
      throw ArgumentError.value(id, 'id', 'Informe o UUID do personagem.');
    }
    final payload = await _getJson(_endpoint(normalizedId));
    return _parseDetails(payload);
  }

  /// POST /api/characters: cria um personagem e recebe a ficha completa (201).
  Future<Character> createCharacter(Map<String, dynamic> data) async {
    final payload = await _writeJson(
      _endpoint(),
      data,
      create: true,
    );
    return _parseDetails(payload);
  }

  /// PATCH /api/characters/{id}: altera apenas os campos informados (200).
  Future<Character> updateCharacter(
    String id,
    Map<String, dynamic> changes,
  ) async {
    final normalizedId = id.trim();
    if (normalizedId.isEmpty) {
      throw ArgumentError.value(id, 'id', 'Informe o UUID do personagem.');
    }
    final payload = await _writeJson(
      _endpoint(normalizedId),
      changes,
      create: false,
    );
    return _parseDetails(payload);
  }

  Character _parseDetails(dynamic payload) {
    if (payload is! Map<String, dynamic>) {
      throw const CharacterApiException(
          'A ficha retornada pela API é inválida.');
    }
    try {
      final character = Character.fromJson(payload);
      if (!character.hasDetails) {
        throw const FormatException(
            'A API não enviou todos os blocos da ficha.');
      }
      return character;
    } on FormatException catch (error) {
      throw CharacterApiException(
          'Ficha do personagem inválida: ${error.message}');
    } on TypeError catch (error) {
      throw CharacterApiException('Ficha do personagem incompatível: $error');
    }
  }

  /// Libera o cliente HTTP quando ele foi criado por este serviço.
  /// Um [client] injetado permanece sob responsabilidade de quem o criou.
  void dispose() {
    if (_ownsClient) _client.close();
  }

  Uri _endpoint([String? characterId]) {
    final path = <String>[
      ..._baseUri.pathSegments.where((segment) => segment.isNotEmpty),
      'api',
      'characters',
      if (characterId != null) characterId,
    ];
    return _baseUri.replace(pathSegments: path);
  }

  Future<dynamic> _getJson(Uri url) async {
    late final http.Response response;
    try {
      response = await _client.get(
        url,
        headers: const {'Accept': 'application/json'},
      ).timeout(requestTimeout);
    } on TimeoutException {
      throw const CharacterApiException(
        'A conexão com o Arconte demorou demais. Confira se a API está ativa.',
      );
    } on http.ClientException catch (error) {
      throw CharacterApiException(
        'Não foi possível conectar ao Arconte. Verifique o FastAPI e o endereço: $error',
      );
    }

    if (response.statusCode != 200) {
      throw CharacterApiException(
        _errorMessage(response),
        statusCode: response.statusCode,
      );
    }

    try {
      // bodyBytes + UTF-8 preserva nomes como ÓFiachra e Sarnília.
      return jsonDecode(utf8.decode(response.bodyBytes));
    } on FormatException {
      throw const CharacterApiException(
        'A API retornou JSON inválido. Verifique a versão do backend.',
      );
    }
  }

  Future<dynamic> _writeJson(
    Uri url,
    Map<String, dynamic> data, {
    required bool create,
  }) async {
    late final http.Response response;
    try {
      final body = jsonEncode(data);
      final headers = <String, String>{
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8',
      };
      response = await (create
              ? _client.post(url, headers: headers, body: body)
              : _client.patch(url, headers: headers, body: body))
          .timeout(requestTimeout);
    } on TimeoutException {
      throw const CharacterApiException(
        'O salvamento demorou demais. Confira a ficha antes de tentar novamente.',
      );
    } on http.ClientException catch (error) {
      throw CharacterApiException(
        'Não foi possível conectar ao Arconte para salvar: $error',
      );
    }

    final expectedStatus = create ? 201 : 200;
    if (response.statusCode != expectedStatus) {
      throw CharacterApiException(
        _errorMessage(response, writing: true),
        statusCode: response.statusCode,
      );
    }

    try {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } on FormatException {
      throw const CharacterApiException(
        'A API retornou JSON inválido após o salvamento.',
      );
    }
  }

  String _errorMessage(http.Response response, {bool writing = false}) {
    String? detail;
    try {
      final payload = jsonDecode(utf8.decode(response.bodyBytes));
      if (payload is Map<String, dynamic>) {
        if (payload['detail'] is String) {
          detail = payload['detail'] as String;
        } else if (payload['detail'] is List) {
          // O FastAPI envia uma lista para erros de validação Pydantic.
          final issues = payload['detail'] as List;
          if (issues.isNotEmpty &&
              issues.first is Map &&
              (issues.first as Map)['msg'] is String) {
            detail = (issues.first as Map)['msg'] as String;
          }
        }
      }
    } on FormatException {
      // Respostas HTTP de erro também podem vir sem JSON.
    }

    if (detail != null && detail.isNotEmpty) return detail;
    switch (response.statusCode) {
      case 404:
        return 'Personagem não encontrado no projeto.';
      case 422:
        return writing
            ? 'Dados inválidos. Confira os campos enviados.'
            : 'O identificador do personagem é inválido.';
      case 503:
        return 'O backend não conseguiu abrir o arquivo do projeto.';
      default:
        return 'Erro HTTP ${response.statusCode} ao consultar o Arconte.';
    }
  }

  static Uri _validateBaseUrl(String url) {
    final parsed = Uri.tryParse(url.trim());
    if (parsed == null ||
        (parsed.scheme != 'http' && parsed.scheme != 'https') ||
        parsed.host.isEmpty ||
        parsed.hasQuery ||
        parsed.hasFragment ||
        parsed.userInfo.isNotEmpty) {
      throw ArgumentError.value(
          url, 'baseUrl', 'Informe uma URL HTTP(S) válida.');
    }
    return parsed;
  }
}
