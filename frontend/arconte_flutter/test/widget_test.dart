import 'dart:convert';

import 'package:arconte_app/app/arconte_app.dart';
import 'package:arconte_app/services/character_api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

const _characterId = '00000000-0000-4000-8000-000000000001';

void _viewport(WidgetTester tester,
    {double width = 1600, double height = 1100}) {
  tester.view.physicalSize = Size(width, height);
  tester.view.devicePixelRatio = 1;
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });
}

/// Simula a API sem abrir conexões: o teste não depende do FastAPI local.
CharacterApi _mockCharacterApi() {
  final client = MockClient((request) async {
    if (request.method == 'GET' && request.url.path == '/api/characters') {
      return http.Response(
        jsonEncode([
          {
            'id': _characterId,
            'name': 'Artuin',
            'surname': 'Hauck',
            'full_name': 'Artuin Hauck',
            'gender': 'Masculino',
            'birth_year': 31,
            'death_year': null,
            'title': 'Conde da Sarnília',
          },
        ]),
        200,
        headers: {'content-type': 'application/json; charset=utf-8'},
      );
    }
    if (request.method == 'GET' &&
        request.url.path == '/api/characters/$_characterId') {
      return http.Response(
        jsonEncode({
          'id': _characterId,
          'name': 'Artuin',
          'surname': 'Hauck',
          'full_name': 'Artuin Hauck',
          'gender': 'Masculino',
          'birth_year': 31,
          'death_year': null,
          'title': 'Conde da Sarnília',
          'biography': 'Conde de Sarnília.',
          'physical': <String, dynamic>{},
          'personality': <String, dynamic>{},
          'social': {'title': 'Conde da Sarnília'},
          'history': {'biography': 'Conde de Sarnília.', 'events': []},
        }),
        200,
        headers: {'content-type': 'application/json; charset=utf-8'},
      );
    }
    return http.Response('{"detail":"Não encontrado"}', 404);
  });
  addTearDown(client.close);
  return CharacterApi(client: client);
}

void main() {
  testWidgets('Exibe a identidade visual e o cartão Personagens',
      (tester) async {
    _viewport(tester);
    await tester.pumpWidget(const ArconteApp());
    expect(find.text('ARCONTE'), findsOneWidget);
    expect(find.text('Onde os mundos ganham vida.'), findsOneWidget);
    expect(find.byKey(const Key('module-card-personagens')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Abre a lista real de personagens e volta ao início',
      (tester) async {
    _viewport(tester);
    await tester.pumpWidget(ArconteApp(characterApi: _mockCharacterApi()));
    await tester.tap(find.byKey(const Key('module-card-personagens')));
    await tester.pumpAndSettle();

    expect(find.text('BIBLIOTECA / PESSOAS'), findsOneWidget);
    expect(find.text('Sua biblioteca de personagens'), findsNothing);
    expect(find.text('Artuin Hauck'), findsOneWidget);
    expect(find.text('Voltar ao códice'), findsOneWidget);
    expect(tester.takeException(), isNull);

    await tester.tap(find.text('Voltar ao códice'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('module-card-personagens')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Abre a ficha completa recebida da API simulada', (tester) async {
    _viewport(tester);
    await tester.pumpWidget(ArconteApp(characterApi: _mockCharacterApi()));
    await tester.tap(find.byKey(const Key('module-card-personagens')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Artuin Hauck'));
    await tester.pumpAndSettle();

    expect(find.text('BIBLIOTECA / PESSOAS / FICHA'), findsOneWidget);
    expect(find.text('O nome nos registros'), findsOneWidget);
    expect(find.text('Conde de Sarnília.'), findsWidgets);
    expect(tester.takeException(), isNull);

    await tester.tap(find.text('Voltar aos personagens'));
    await tester.pumpAndSettle();
    expect(find.text('BIBLIOTECA / PESSOAS'), findsOneWidget);
  });

  testWidgets('Módulos ainda não conectados continuam com placeholder',
      (tester) async {
    _viewport(tester);
    await tester.pumpWidget(const ArconteApp());
    await tester.tap(find.byKey(const Key('module-card-genealogias')));
    await tester.pumpAndSettle();

    expect(find.text('Sua biblioteca de genealogias'), findsOneWidget);
    expect(find.textContaining('integração pendente'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  for (final width in <double>[800, 1150, 1600]) {
    testWidgets('Painel sem estouros de layout na largura ${width.toInt()}',
        (tester) async {
      _viewport(tester, width: width, height: 1100);
      await tester.pumpWidget(const ArconteApp());
      await tester.pumpAndSettle();
      expect(find.text('Onde os mundos ganham vida.'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }
}
