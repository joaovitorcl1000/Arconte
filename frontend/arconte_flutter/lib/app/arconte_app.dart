import 'package:flutter/material.dart';

import '../screens/workspace_screen.dart';
import '../services/character_api.dart';
import '../theme/arconte_theme.dart';

class ArconteApp extends StatelessWidget {
  const ArconteApp({super.key, this.characterApi});

  /// Serviço opcional: permite testar a navegação sem acesso HTTP real.
  final CharacterApi? characterApi;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Arconte • Ateliê de Mundos',
      debugShowCheckedModeBanner: false,
      theme: ArconteTheme.light,
      home: WorkspaceScreen(characterApi: characterApi),
    );
  }
}
