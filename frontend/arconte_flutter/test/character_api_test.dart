import 'dart:convert';

import 'package:arconte_app/services/character_api.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

const _characterId = 'c0ba4a0b-6933-4f96-840c-3d499aa107d2';

Map<String, dynamic> _detail({
  String name = 'Sofia',
  String? title,
}) {
  return {
    'id': _characterId,
    'name': name,
    'surname': 'Hauck',
    'full_name': '$name Hauck',
    'gender': null,
    'birth_year': 48,
    'death_year': null,
    'title': title,
    'biography': null,
    'physical': <String, dynamic>{},
    'personality': <String, dynamic>{},
    'social': <String, dynamic>{'title': title},
    'history': <String, dynamic>{'events': <dynamic>[]},
  };
}

http.Response _jsonResponse(Object payload, int statusCode) {
  return http.Response(
    jsonEncode(payload),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

void main() {
  group('CharacterApi - leitura existente', () {
    test('GET lista personagens sem exigir ficha completa', () async {
      final client = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/api/characters');
        return _jsonResponse([
          {
            'id': _characterId,
            'name': 'Sofia',
            'surname': 'Hauck',
            'full_name': 'Sofia Hauck',
          }
        ], 200);
      });
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      final characters = await api.getCharacters();
      expect(characters, hasLength(1));
      expect(characters.single.fullName, 'Sofia Hauck');
      expect(characters.single.hasDetails, isFalse);
    });

    test('GET obtém ficha completa sem alterar o UUID', () async {
      final client = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/api/characters/$_characterId');
        return _jsonResponse(_detail(), 200);
      });
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      final character = await api.getCharacter(_characterId);
      expect(character.id, _characterId);
      expect(character.hasDetails, isTrue);
    });
  });

  group('CharacterApi - criação', () {
    test('POST envia JSON e aceita resposta 201 com ficha completa', () async {
      final client = MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, '/api/characters');
        expect(request.headers['content-type'], contains('application/json'));
        expect(request.headers['accept'], 'application/json');

        final sent = jsonDecode(request.body) as Map<String, dynamic>;
        expect(sent['name'], 'Sofia');
        expect(sent['surname'], 'Hauck');
        expect(
            (sent['physical'] as Map<String, dynamic>)['hair_color'], 'Ruivo');
        return _jsonResponse(_detail(), 201);
      });
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      final saved = await api.createCharacter({
        'name': 'Sofia',
        'surname': 'Hauck',
        'physical': {'hair_color': 'Ruivo'},
      });
      expect(saved.id, _characterId);
      expect(saved.name, 'Sofia');
      expect(saved.hasDetails, isTrue);
    });

    test('POST rejeita erro de validação 422 com lista do FastAPI', () async {
      final client = MockClient((request) async => _jsonResponse({
            'detail': [
              {
                'loc': ['body', 'name'],
                'msg': 'Nome obrigatório',
                'type': 'value_error',
              }
            ]
          }, 422));
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      await expectLater(
        api.createCharacter({'name': ''}),
        throwsA(isA<CharacterApiException>()
            .having((e) => e.statusCode, 'statusCode', 422)
            .having((e) => e.message, 'message', contains('Nome obrigatório'))),
      );
    });

    test('POST só aceita 201 como criação bem-sucedida', () async {
      final client =
          MockClient((request) async => _jsonResponse(_detail(), 200));
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      await expectLater(
        api.createCharacter({'name': 'Sofia'}),
        throwsA(isA<CharacterApiException>()
            .having((e) => e.statusCode, 'statusCode', 200)),
      );
    });
  });

  group('CharacterApi - edição', () {
    test('PATCH envia somente a mudança e mantém o UUID da resposta', () async {
      final client = MockClient((request) async {
        expect(request.method, 'PATCH');
        expect(request.url.path, '/api/characters/$_characterId');
        expect(jsonDecode(request.body), {
          'social': {'title': 'Condessa'},
        });
        return _jsonResponse(_detail(title: 'Condessa'), 200);
      });
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      final saved = await api.updateCharacter(_characterId, {
        'social': {'title': 'Condessa'},
      });
      expect(saved.id, _characterId);
      expect(saved.social?.title, 'Condessa');
      expect(saved.name, 'Sofia');
    });

    test('PATCH rejeita UUID vazio antes de enviar a requisição', () async {
      final client = MockClient((request) async {
        fail('Não deveria enviar requisição para UUID vazio.');
      });
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      await expectLater(
        api.updateCharacter('   ', {'name': 'Outra'}),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('PATCH devolve erro HTTP 404 para personagem inexistente', () async {
      final client = MockClient((request) async => _jsonResponse(
            {'detail': 'Personagem não encontrado neste projeto.'},
            404,
          ));
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      await expectLater(
        api.updateCharacter(_characterId, {'name': 'Outra'}),
        throwsA(isA<CharacterApiException>()
            .having((e) => e.statusCode, 'statusCode', 404)
            .having((e) => e.message, 'message', contains('não encontrado'))),
      );
    });

    test('PATCH transmite a mensagem de erro 400 do backend', () async {
      final client = MockClient((request) async => _jsonResponse(
            {'detail': 'Ano de falecimento inválido.'},
            400,
          ));
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      await expectLater(
        api.updateCharacter(_characterId, {'death_year': -2}),
        throwsA(isA<CharacterApiException>()
            .having((e) => e.statusCode, 'statusCode', 400)
            .having((e) => e.message, 'message', contains('falecimento'))),
      );
    });
  });

  group('CharacterApi - respostas inválidas', () {
    test('falha se o POST não devolver os quatro blocos da ficha', () async {
      final client = MockClient((request) async => _jsonResponse({
            'id': _characterId,
            'name': 'Sofia',
            'full_name': 'Sofia Hauck',
          }, 201));
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      await expectLater(
        api.createCharacter({'name': 'Sofia'}),
        throwsA(isA<CharacterApiException>()
            .having((e) => e.message, 'message', contains('blocos'))),
      );
    });

    test('falha de transporte é convertida em CharacterApiException', () async {
      final client = MockClient((request) async {
        throw http.ClientException('conexão indisponível');
      });
      addTearDown(client.close);
      final api = CharacterApi(client: client);
      addTearDown(api.dispose);

      await expectLater(
        api.createCharacter({'name': 'Sofia'}),
        throwsA(isA<CharacterApiException>()
            .having((e) => e.message, 'message', contains('conectar'))),
      );
    });
  });
}
