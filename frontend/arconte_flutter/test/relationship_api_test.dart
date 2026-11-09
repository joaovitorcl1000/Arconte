import 'dart:async';
import 'dart:convert';

import 'package:arconte_app/services/relationship_api.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

// UUIDs fictícios: os testes não consultam o backend nem o arquivo da Sarnília.
const _parentId = '11111111-1111-4111-8111-111111111111';
const _childId = '22222222-2222-4222-8222-222222222222';
const _relationshipId = '33333333-3333-4333-8333-333333333333';

Map<String, dynamic> _record({
  String type = 'biological_parent',
  bool? directed,
  int? startYear,
  int? endYear,
}) {
  return {
    'id': _relationshipId,
    'source_id': _parentId,
    'target_id': _childId,
    'source_name': 'Álvaro d\'Ávila',
    'target_name': 'Sofia Hauck',
    'type': type,
    'is_directed':
        directed ?? (type == 'biological_parent' || type == 'adoptive_parent'),
    'start_year': startYear,
    'end_year': endYear,
  };
}

http.Response _json(Object payload, int code) => http.Response(
      jsonEncode(payload),
      code,
      headers: const {'content-type': 'application/json; charset=utf-8'},
    );

/// Injeta um cliente simulado; o Arconte real nunca é acessado.
RelationshipApi _apiWith(
  Future<http.Response> Function(http.Request) handler, {
  String baseUrl = 'http://127.0.0.1:8000',
  Duration timeout = const Duration(seconds: 10),
}) {
  final client = MockClient(handler);
  addTearDown(client.close);
  final api = RelationshipApi(
    baseUrl: baseUrl,
    client: client,
    requestTimeout: timeout,
  );
  addTearDown(api.dispose);
  return api;
}

void main() {
  group('RelationshipRecord - contrato JSON', () {
    test('interpreta nomes UTF-8, UUIDs, direção e datas opcionais', () {
      final relationship = RelationshipRecord.fromJson(
        _record(startYear: 43, endYear: 56),
      );
      expect(relationship.id, _relationshipId);
      expect(relationship.sourceId, _parentId);
      expect(relationship.targetId, _childId);
      expect(relationship.sourceName, 'Álvaro d\'Ávila');
      expect(relationship.targetName, 'Sofia Hauck');
      expect(relationship.type, 'biological_parent');
      expect(relationship.isDirected, isTrue);
      expect(relationship.startYear, 43);
      expect(relationship.endYear, 56);
    });

    test('reconhece os quatro tipos e a direção declarada pelo backend', () {
      for (final type in [
        'biological_parent',
        'adoptive_parent',
        'marriage',
        'partnership',
      ]) {
        final relationship = RelationshipRecord.fromJson(_record(type: type));
        expect(relationship.type, type);
        expect(
          relationship.isDirected,
          type == 'biological_parent' || type == 'adoptive_parent',
        );
        expect(relationship.startYear, isNull);
        expect(relationship.endYear, isNull);
      }
    });

    test('rejeita campos obrigatórios ausentes ou inválidos', () {
      for (final changes in <Map<String, dynamic>>[
        {'id': ''},
        {'source_id': null},
        {'target_name': 123},
        {'is_directed': 'sim'},
        {'type': 'unknown'},
        {'start_year': '42'},
        {'end_year': 2.5},
      ]) {
        expect(
          () => RelationshipRecord.fromJson({..._record(), ...changes}),
          throwsFormatException,
          reason: 'Campos inválidos não podem ser aceitos: $changes',
        );
      }
    });
  });

  group('RelationshipApi - consulta GET', () {
    test('consulta apenas os vínculos do personagem, preservando UTF-8',
        () async {
      final api = _apiWith((request) async {
        expect(request.method, 'GET');
        expect(request.url.toString(),
            'http://127.0.0.1:8000/api/characters/$_childId/relationships');
        expect(request.headers['accept'], 'application/json');
        return _json([_record(startYear: 25)], 200);
      });

      final relationships = await api.getRelationships(_childId);
      expect(relationships, hasLength(1));
      expect(relationships.single.sourceName, 'Álvaro d\'Ávila');
      expect(relationships.single.startYear, 25);
      expect(() => relationships.clear(), throwsUnsupportedError);
    });

    test('aceita uma lista vazia', () async {
      final api = _apiWith((request) async => _json([], 200));
      expect(await api.getRelationships(_childId), isEmpty);
    });

    test('rejeita identificador vazio antes da chamada HTTP', () async {
      final api = _apiWith((request) async {
        fail('Não deveria fazer requisições com UUID vazio.');
      });
      await expectLater(api.getRelationships('  '), throwsArgumentError);
    });

    test('rejeita envelope JSON que não seja uma lista', () async {
      final api = _apiWith((request) async => _json(_record(), 200));
      await expectLater(
        api.getRelationships(_childId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.message, 'message', contains('lista'))),
      );
    });

    test('rejeita itens inválidos dentro da lista', () async {
      final api = _apiWith((request) async => _json([_record(), 7], 200));
      await expectLater(
        api.getRelationships(_childId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.message, 'message', contains('inválido'))),
      );
    });

    test('rejeita um registro com tipo desconhecido', () async {
      final api = _apiWith(
        (request) async => _json([_record(type: 'friendship')], 200),
      );
      await expectLater(
        api.getRelationships(_childId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.message, 'message', contains('desconhecido'))),
      );
    });

    test('propaga 404 e a descrição enviada pelo FastAPI', () async {
      final api = _apiWith((request) async => _json(
            {'detail': 'Personagem não encontrado neste projeto.'},
            404,
          ));
      await expectLater(
        api.getRelationships(_childId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 404)
            .having((e) => e.message, 'message', contains('não encontrado'))),
      );
    });

    test('não aceita status 201 em lugar do 200 esperado', () async {
      final api = _apiWith((request) async => _json([], 201));
      await expectLater(
        api.getRelationships(_childId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 201)),
      );
    });

    test('rejeita JSON inválido em resposta de sucesso', () async {
      final api = _apiWith((request) async => http.Response('{inválido', 200));
      await expectLater(
        api.getRelationships(_childId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.message, 'message', contains('JSON inválido'))),
      );
    });
  });

  group('RelationshipApi - criação POST', () {
    test('envia IDs, tipo e anos em JSON e aceita HTTP 201', () async {
      final api = _apiWith((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, '/api/relationships');
        expect(request.headers['accept'], 'application/json');
        expect(request.headers['content-type'], contains('application/json'));
        expect(jsonDecode(request.body), {
          'source_id': _parentId,
          'target_id': _childId,
          'type': 'adoptive_parent',
          'start_year': 50,
          'end_year': null,
        });
        return _json(_record(type: 'adoptive_parent', startYear: 50), 201);
      });

      final created = await api.createRelationship({
        'source_id': _parentId,
        'target_id': _childId,
        'type': 'adoptive_parent',
        'start_year': 50,
        'end_year': null,
      });
      expect(created.id, _relationshipId);
      expect(created.type, 'adoptive_parent');
      expect(created.isDirected, isTrue);
      expect(created.startYear, 50);
    });

    test('aceita casamento simétrico com os IDs retornados pelo backend',
        () async {
      final api = _apiWith((request) async {
        expect(jsonDecode(request.body)['type'], 'marriage');
        return _json(_record(type: 'marriage', directed: false), 201);
      });
      final created = await api.createRelationship({
        'source_id': _childId,
        'target_id': _parentId,
        'type': 'marriage',
      });
      expect(created.isDirected, isFalse);
      expect(created.sourceId, _parentId);
      expect(created.targetId, _childId);
    });

    test('propaga mensagem de validação 422 com detail em string', () async {
      final api = _apiWith((request) async => _json(
            {'detail': 'Essa filiação produziria um ciclo genealógico.'},
            422,
          ));
      await expectLater(
        api.createRelationship({
          'source_id': _parentId,
          'target_id': _childId,
          'type': 'biological_parent',
        }),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 422)
            .having(
                (e) => e.message, 'message', contains('ciclo genealógico'))),
      );
    });

    test('propaga primeira mensagem em lista de erros Pydantic', () async {
      final api = _apiWith((request) async => _json({
            'detail': [
              {
                'loc': ['body', 'source_id'],
                'msg': 'UUID inválido',
                'type': 'uuid_parsing',
              }
            ]
          }, 422));
      await expectLater(
        api.createRelationship({'source_id': 'inválido'}),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 422)
            .having((e) => e.message, 'message', contains('UUID inválido'))),
      );
    });

    test('preserva erro 404 quando algum personagem não existe', () async {
      final api = _apiWith((request) async => _json(
            {'detail': 'Um dos personagens não existe neste projeto.'},
            404,
          ));
      await expectLater(
        api.createRelationship({'source_id': _parentId}),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 404)),
      );
    });

    test('não trata HTTP 200 como criação bem-sucedida', () async {
      final api = _apiWith((request) async => _json(_record(), 200));
      await expectLater(
        api.createRelationship({'type': 'partnership'}),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 200)),
      );
    });

    test('rejeita resposta 201 que não seja objeto JSON', () async {
      final api = _apiWith((request) async => _json([_record()], 201));
      await expectLater(
        api.createRelationship({'type': 'partnership'}),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.message, 'message', contains('formato inválido'))),
      );
    });

    test('rejeita resposta 201 com relação incompleta', () async {
      final api =
          _apiWith((request) async => _json({'id': _relationshipId}, 201));
      await expectLater(
        api.createRelationship({'type': 'partnership'}),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.message, 'message', contains('inválido'))),
      );
    });
  });

  group('RelationshipApi - remoção DELETE', () {
    test('usa o UUID na URL e aceita HTTP 204 sem corpo', () async {
      final api = _apiWith((request) async {
        expect(request.method, 'DELETE');
        expect(request.url.path, '/api/relationships/$_relationshipId');
        expect(request.headers['accept'], 'application/json');
        return http.Response('', 204);
      });
      await api.deleteRelationship(_relationshipId);
    });

    test('rejeita identificador vazio antes de chamar o servidor', () async {
      final api = _apiWith((request) async {
        fail('Não deveria chamar DELETE com UUID vazio.');
      });
      await expectLater(api.deleteRelationship(' '), throwsArgumentError);
    });

    test('retorna erro 404 quando o vínculo não existe', () async {
      final api = _apiWith((request) async => _json(
            {'detail': 'Relacionamento não encontrado neste projeto.'},
            404,
          ));
      await expectLater(
        api.deleteRelationship(_relationshipId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 404)
            .having((e) => e.message, 'message', contains('não encontrado'))),
      );
    });

    test('não aceita HTTP 200 como remoção bem-sucedida', () async {
      final api = _apiWith((request) async => _json({}, 200));
      await expectLater(
        api.deleteRelationship(_relationshipId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 200)),
      );
    });

    test('trata erro 503 sem JSON com mensagem apropriada', () async {
      final api = _apiWith(
        (request) async => http.Response('Serviço indisponível', 503),
      );
      await expectLater(
        api.deleteRelationship(_relationshipId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.statusCode, 'statusCode', 503)
            .having((e) => e.message, 'message', contains('backend'))),
      );
    });
  });

  group('RelationshipApi - configuração e falhas de transporte', () {
    test('respeita prefixo informado na URL-base', () async {
      final api = _apiWith(
        (request) async {
          expect(request.url.path,
              '/arconte/api/characters/$_childId/relationships');
          return _json([], 200);
        },
        baseUrl: 'https://localhost:8443/arconte',
      );
      expect(await api.getRelationships(_childId), isEmpty);
    });

    test('rejeita URL-base inválida e timeout não positivo', () {
      for (final url in [
        '',
        'not-a-url',
        'ftp://localhost:8000',
        'http://localhost:8000?token=1',
        'http://user:password@localhost:8000',
      ]) {
        expect(() => RelationshipApi(baseUrl: url), throwsArgumentError);
      }
      expect(
        () => RelationshipApi(requestTimeout: Duration.zero),
        throwsArgumentError,
      );
    });

    test('converte falha da conexão HTTP em exceção do serviço', () async {
      final api = _apiWith((request) async {
        throw http.ClientException('sem conexão');
      });
      await expectLater(
        api.getRelationships(_childId),
        throwsA(isA<RelationshipApiException>()
            .having((e) => e.message, 'message', contains('conectar'))),
      );
    });

    test('trata timeout com mensagem que evita repetição de gravação',
        () async {
      final pending = Completer<http.Response>();
      final api = _apiWith(
        (request) => pending.future,
        timeout: const Duration(milliseconds: 20),
      );
      await expectLater(
        api.createRelationship({'type': 'marriage'}),
        throwsA(isA<RelationshipApiException>().having(
            (e) => e.message, 'message', contains('Verifique o resultado'))),
      );
    });
  });
}
