/// Cliente HTTP dos vínculos familiares do Arconte.
///
/// Reutiliza as rotas do FastAPI, sem reproduzir as regras genealógicas
/// existentes no backend Python:
///
///   GET    /api/characters/{character_id}/relationships
///   POST   /api/relationships
///   DELETE /api/relationships/{relationship_id}
///
/// Dependência já utilizada pelo projeto Flutter: package:http.
/// Para Flutter Web local, o FastAPI deve estar ativo em 127.0.0.1:8000.

import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

/// Registro de vínculo tal como devolvido pelo FastAPI.
///
/// Em filiações, sourceId identifica o responsável e targetId o filho.
/// Casamentos e uniões não possuem direção e os IDs são normalizados
/// pelo backend; não dependa da ordem recebida para identificar o parceiro.
class RelationshipRecord {
  const RelationshipRecord({
    required this.id,
    required this.sourceId,
    required this.targetId,
    required this.sourceName,
    required this.targetName,
    required this.type,
    required this.isDirected,
    required this.startYear,
    required this.endYear,
  });

  final String id;
  final String sourceId;
  final String targetId;
  final String sourceName;
  final String targetName;

  /// biological_parent, adoptive_parent, marriage ou partnership.
  final String type;
  final bool isDirected;
  final int? startYear;
  final int? endYear;

  factory RelationshipRecord.fromJson(Map<String, dynamic> json) {
    String text(String field) {
      final value = json[field];
      if (value is! String || value.trim().isEmpty) {
        throw FormatException('Campo $field ausente ou inválido.');
      }
      return value;
    }

    int? year(String field) {
      final value = json[field];
      if (value == null) return null;
      if (value is! int) {
        throw FormatException('Campo $field deve ser um ano inteiro ou null.');
      }
      return value;
    }

    final directed = json['is_directed'];
    if (directed is! bool) {
      throw const FormatException('Campo is_directed ausente ou inválido.');
    }

    final kind = text('type');
    if (!const {
      'biological_parent',
      'adoptive_parent',
      'marriage',
      'partnership',
    }.contains(kind)) {
      throw FormatException('Tipo de relacionamento desconhecido: $kind.');
    }

    return RelationshipRecord(
      id: text('id'),
      sourceId: text('source_id'),
      targetId: text('target_id'),
      sourceName: text('source_name'),
      targetName: text('target_name'),
      type: kind,
      isDirected: directed,
      startYear: year('start_year'),
      endYear: year('end_year'),
    );
  }
}

class RelationshipApiException implements Exception {
  const RelationshipApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => statusCode == null
      ? 'RelationshipApiException: $message'
      : 'RelationshipApiException ($statusCode): $message';
}

class RelationshipApi {
  RelationshipApi({
    String baseUrl = 'http://127.0.0.1:8000',
    http.Client? client,
    this.requestTimeout = const Duration(seconds: 10),
  })  : _baseUri = _validateBaseUrl(baseUrl),
        _client = client ?? http.Client(),
        _ownsClient = client == null {
    if (requestTimeout <= Duration.zero) {
      throw ArgumentError.value(
        requestTimeout,
        'requestTimeout',
        'Deve ser positivo.',
      );
    }
  }

  final Uri _baseUri;
  final http.Client _client;
  final bool _ownsClient;
  final Duration requestTimeout;

  /// Lista apenas os vínculos do personagem informado (HTTP 200).
  Future<List<RelationshipRecord>> getRelationships(String characterId) async {
    final id = _requiredId(characterId, 'characterId');
    final url = _endpoint(['characters', id, 'relationships']);
    final response = await _send('GET', url);
    _requireStatus(response, 200);
    final payload = _decodeJson(response);
    if (payload is! List) {
      throw const RelationshipApiException(
        'A API retornou uma lista de relacionamentos inválida.',
      );
    }
    try {
      return List<RelationshipRecord>.unmodifiable(payload.map((item) {
        if (item is! Map<String, dynamic>) {
          throw const FormatException('Registro de relacionamento inválido.');
        }
        return RelationshipRecord.fromJson(item);
      }));
    } on FormatException catch (error) {
      throw RelationshipApiException(
        'Dados de relacionamentos inválidos: ${error.message}',
      );
    } on TypeError catch (error) {
      throw RelationshipApiException('Dados incompatíveis: $error');
    }
  }

  /// Cria um vínculo e devolve o registro com UUID e nomes (HTTP 201).
  ///
  /// Exemplo:
  ///   await api.createRelationship({
  ///     'source_id': parentId,
  ///     'target_id': childId,
  ///     'type': 'biological_parent',
  ///     'start_year': null,
  ///     'end_year': null,
  ///   });
  ///
  /// Valores possíveis para type: biological_parent, adoptive_parent,
  /// marriage e partnership. O backend valida duplicatas, ciclos e datas.
  Future<RelationshipRecord> createRelationship(Map<String, dynamic> data) async {
    final url = _endpoint(['relationships']);
    final response = await _send('POST', url, body: data);
    _requireStatus(response, 201);
    final payload = _decodeJson(response);
    if (payload is! Map<String, dynamic>) {
      throw const RelationshipApiException(
        'A API retornou um relacionamento em formato inválido.',
      );
    }
    try {
      return RelationshipRecord.fromJson(payload);
    } on FormatException catch (error) {
      throw RelationshipApiException(
        'Relacionamento retornado inválido: ${error.message}',
      );
    } on TypeError catch (error) {
      throw RelationshipApiException('Relacionamento incompatível: $error');
    }
  }

  /// Exclui apenas o vínculo, preservando os personagens (HTTP 204).
  /// Respostas 204 não têm corpo JSON.
  Future<void> deleteRelationship(String relationshipId) async {
    final id = _requiredId(relationshipId, 'relationshipId');
    final url = _endpoint(['relationships', id]);
    final response = await _send('DELETE', url);
    _requireStatus(response, 204);
  }

  /// Fecha somente o cliente HTTP criado internamente.
  /// Clientes injetados para testes continuam pertencendo ao chamador.
  void dispose() {
    if (_ownsClient) _client.close();
  }

  Uri _endpoint(List<String> segments) {
    return _baseUri.replace(pathSegments: [
      ..._baseUri.pathSegments.where((segment) => segment.isNotEmpty),
      'api',
      ...segments,
    ]);
  }

  Future<http.Response> _send(
    String method,
    Uri url, {
    Map<String, dynamic>? body,
  }) async {
    final headers = <String, String>{
      'Accept': 'application/json',
      if (body != null) 'Content-Type': 'application/json; charset=utf-8',
    };

    try {
      switch (method) {
        case 'GET':
          return await _client.get(url, headers: headers).timeout(requestTimeout);
        case 'POST':
          return await _client
              .post(url, headers: headers, body: jsonEncode(body))
              .timeout(requestTimeout);
        case 'DELETE':
          return await _client.delete(url, headers: headers).timeout(requestTimeout);
        default:
          throw StateError('Método HTTP não suportado: $method');
      }
    } on TimeoutException {
      throw const RelationshipApiException(
        'A conexão demorou demais. Verifique o resultado antes de tentar novamente.',
      );
    } on http.ClientException catch (error) {
      throw RelationshipApiException(
        'Não foi possível conectar ao Arconte. Verifique o FastAPI: $error',
      );
    }
  }

  void _requireStatus(http.Response response, int expected) {
    if (response.statusCode == expected) return;
    throw RelationshipApiException(
      _errorMessage(response),
      statusCode: response.statusCode,
    );
  }

  dynamic _decodeJson(http.Response response) {
    try {
      // Decodifica bytes explicitamente em UTF-8 para preservar acentos.
      return jsonDecode(utf8.decode(response.bodyBytes));
    } on FormatException {
      throw const RelationshipApiException(
        'A API retornou JSON inválido. Verifique a versão do backend.',
      );
    }
  }

  String _errorMessage(http.Response response) {
    try {
      final payload = jsonDecode(utf8.decode(response.bodyBytes));
      if (payload is Map<String, dynamic>) {
        final detail = payload['detail'];
        if (detail is String && detail.isNotEmpty) return detail;
        if (detail is List && detail.isNotEmpty) {
          final first = detail.first;
          if (first is Map && first['msg'] is String) {
            return first['msg'] as String;
          }
        }
      }
    } on FormatException {
      // O servidor pode devolver erros sem JSON.
    }

    switch (response.statusCode) {
      case 404:
        return 'Personagem ou relacionamento não encontrado no projeto.';
      case 422:
        return 'Dados inválidos ou vínculo não permitido. Confira os campos.';
      case 503:
        return 'O backend não conseguiu acessar ou salvar o projeto.';
      default:
        return 'Erro HTTP ${response.statusCode} na API de relacionamentos.';
    }
  }

  static String _requiredId(String value, String name) {
    final normalized = value.trim();
    if (normalized.isEmpty) {
      throw ArgumentError.value(value, name, 'Informe o UUID.');
    }
    return normalized;
  }

  static Uri _validateBaseUrl(String url) {
    final parsed = Uri.tryParse(url.trim());
    if (parsed == null ||
        (parsed.scheme != 'http' && parsed.scheme != 'https') ||
        parsed.host.isEmpty ||
        parsed.hasQuery ||
        parsed.hasFragment ||
        parsed.userInfo.isNotEmpty) {
      throw ArgumentError.value(url, 'baseUrl', 'Informe uma URL HTTP(S) válida.');
    }
    return parsed;
  }
}
