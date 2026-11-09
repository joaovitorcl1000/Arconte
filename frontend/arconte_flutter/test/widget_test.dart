import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:arconte_app/app/arconte_app.dart';

void main() {
  testWidgets('Exibe a identidade visual e os módulos do Arconte',
      (tester) async {
    tester.view.physicalSize = const Size(1600, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
    await tester.pumpWidget(const ArconteApp());
    expect(find.text('ARCONTE'), findsOneWidget);
    expect(find.text('Onde os mundos ganham vida.'), findsOneWidget);
    expect(find.byKey(const Key('module-card-personagens')), findsOneWidget);
  });

  testWidgets('Abre o placeholder de um módulo sem backend', (tester) async {
    tester.view.physicalSize = const Size(1600, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
    await tester.pumpWidget(const ArconteApp());
    await tester.tap(find.byKey(const Key('module-card-personagens')));
    await tester.pumpAndSettle();
    expect(find.text('Sua biblioteca de personagens'), findsOneWidget);
    expect(find.textContaining('integração pendente'), findsOneWidget);
  });
}
