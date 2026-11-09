import 'package:flutter/material.dart';

import '../../models/character.dart';
import '../../services/character_api.dart';
import '../../theme/arconte_theme.dart';
import '../../widgets/ornaments.dart';
import 'character_details.dart';
import 'character_form.dart';

/// Biblioteca de personagens do mundo selecionado.
///
/// Esta tela é incorporada no WorkspaceScreen (sem Scaffold próprio).
/// Consulta exclusivamente a API FastAPI, sem personagens fictícios embutidos.
///
/// Exemplo de uso:
///   CharactersScreen(onBack: goHome)
///
/// [api] é opcional para permitir testes com um serviço injetado. Quando uma
/// instância é recebida, sua vida útil continua sob responsabilidade de quem a
/// criou. Caso contrário, a tela cria e descarta seu próprio CharacterApi.
class CharactersScreen extends StatefulWidget {
  const CharactersScreen({super.key, this.onBack, this.api});

  final VoidCallback? onBack;
  final CharacterApi? api;

  @override
  State<CharactersScreen> createState() => _CharactersScreenState();
}

class _CharactersScreenState extends State<CharactersScreen> {
  late final CharacterApi _api;
  late final bool _ownsApi;

  final TextEditingController _searchController = TextEditingController();
  List<Character> _characters = const [];
  String _search = '';
  String? _error;
  String? _selectedId;
  bool _creating = false;
  bool _loading = true;
  int _generation = 0;

  @override
  void initState() {
    super.initState();
    _ownsApi = widget.api == null;
    _api = widget.api ?? CharacterApi();
    _loadCharacters();
  }

  @override
  void dispose() {
    _generation++;
    _searchController.dispose();
    if (_ownsApi) _api.dispose();
    super.dispose();
  }

  Future<void> _loadCharacters() async {
    final generation = ++_generation;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final characters = await _api.getCharacters();
      if (!mounted || generation != _generation) return;
      setState(() {
        _characters = characters;
        _loading = false;
      });
    } catch (error) {
      if (!mounted || generation != _generation) return;
      setState(() {
        _error = _readableError(error);
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_creating) {
      return CharacterForm(
        api: _api,
        onCancel: () => setState(() => _creating = false),
        onSaved: (person) {
          setState(() {
            _creating = false;
            _selectedId = person.id;
          });
          // Recarrega os registros para incluir o personagem recém-criado.
          _loadCharacters();
        },
      );
    }

    if (_selectedId != null) {
      return CharacterDetails(
        key: ValueKey(_selectedId),
        characterId: _selectedId!,
        api: _api,
        onBack: () => setState(() => _selectedId = null),
      );
    }

    final query = _search.trim().toLowerCase();
    final filtered = _characters.where((character) {
      if (query.isEmpty) return true;
      final terms = <String>[
        character.fullName,
        character.title ?? '',
        character.gender ?? '',
      ].join(' ').toLowerCase();
      return terms.contains(query);
    }).toList(growable: false);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.onBack != null) ...[
          TextButton.icon(
            onPressed: widget.onBack,
            icon: const Icon(Icons.arrow_back, size: 17),
            label: const Text('Voltar ao códice'),
            style: TextButton.styleFrom(foregroundColor: ArconteColors.forest),
          ),
          const SizedBox(height: 20),
        ],
        const SmallCaps('BIBLIOTECA / PESSOAS',
            color: ArconteColors.forestLight),
        const SizedBox(height: 11),
        const Text('Personagens', style: ArconteType.display),
        const SizedBox(height: 10),
        const Text(
          'Vidas, memórias e destinos registrados nos anais do seu mundo.',
          style: TextStyle(fontSize: 15, color: ArconteColors.secondaryText),
        ),
        const SizedBox(height: 24),
        const DecorativeRule(width: 115),
        const SizedBox(height: 29),
        _libraryToolbar(),
        const SizedBox(height: 21),
        if (_loading)
          const _InfoPanel(
            icon: Icons.auto_stories_outlined,
            title: 'Abrindo os registros...',
            description: 'Consultando os personagens no arquivo do mundo.',
            loading: true,
          )
        else if (_error != null)
          _InfoPanel(
            icon: Icons.wifi_off_rounded,
            title: 'Não foi possível consultar os personagens',
            description: _error!,
            actionLabel: 'Tentar novamente',
            onAction: _loadCharacters,
          )
        else if (_characters.isEmpty)
          const _InfoPanel(
            icon: Icons.menu_book_outlined,
            title: 'O códice ainda está vazio',
            description:
                'Nenhum personagem foi encontrado no projeto carregado pela API.',
          )
        else if (filtered.isEmpty)
          _InfoPanel(
            icon: Icons.search_off_outlined,
            title: 'Nenhum personagem encontrado',
            description:
                'A busca não encontrou resultados. Experimente outro nome ou título.',
            actionLabel: 'Limpar busca',
            onAction: () {
              _searchController.clear();
              setState(() => _search = '');
            },
          )
        else ...[
          Text(
            '${filtered.length} ${filtered.length == 1 ? 'registro encontrado' : 'registros encontrados'}',
            style: const TextStyle(
              color: ArconteColors.secondaryText,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 13),
          // A rolagem é gerenciada pelo SingleChildScrollView do WorkspaceScreen.
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: filtered.length,
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final person = filtered[index];
              return _CharacterCard(
                character: person,
                onTap: () => setState(() => _selectedId = person.id),
              );
            },
          ),
        ],
        const SizedBox(height: 30),
      ],
    );
  }

  Widget _libraryToolbar() {
    return LayoutBuilder(builder: (context, constraints) {
      final narrow = constraints.maxWidth < 760;
      final search = TextField(
        controller: _searchController,
        onChanged: (value) => setState(() => _search = value),
        textInputAction: TextInputAction.search,
        decoration: InputDecoration(
          hintText: 'Buscar por nome ou título...',
          prefixIcon:
              const Icon(Icons.search, color: ArconteColors.forestLight),
          suffixIcon: _searchController.text.isEmpty
              ? null
              : IconButton(
                  tooltip: 'Limpar busca',
                  onPressed: () {
                    _searchController.clear();
                    setState(() => _search = '');
                  },
                  icon: const Icon(Icons.close, size: 18),
                ),
        ),
      );
      final refresh = OutlinedButton.icon(
        onPressed: _loading ? null : _loadCharacters,
        icon: const Icon(Icons.refresh, size: 18),
        label: const Text('Atualizar registros'),
        style: OutlinedButton.styleFrom(
          foregroundColor: ArconteColors.forest,
          side: const BorderSide(color: ArconteColors.border),
          padding: const EdgeInsets.symmetric(horizontal: 17, vertical: 17),
        ),
      );
      final create = FilledButton.icon(
        key: const Key('new-character-button'),
        onPressed: () => setState(() => _creating = true),
        icon: const Icon(Icons.person_add_alt_1_outlined, size: 18),
        label: const Text('Novo personagem'),
        style: FilledButton.styleFrom(
          backgroundColor: ArconteColors.forest,
          foregroundColor: ArconteColors.paleGold,
          padding: const EdgeInsets.symmetric(horizontal: 17, vertical: 17),
        ),
      );
      return narrow
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                search,
                const SizedBox(height: 12),
                refresh,
                const SizedBox(height: 12),
                create,
              ],
            )
          : Row(children: [
              Expanded(child: search),
              const SizedBox(width: 13),
              refresh,
              const SizedBox(width: 13),
              create,
            ]);
    });
  }
}

class _CharacterCard extends StatelessWidget {
  const _CharacterCard({required this.character, required this.onTap});

  final Character character;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final subtitle = character.title?.trim().isNotEmpty == true
        ? character.title!
        : 'Registro de personagem';
    final dates = character.birthYear == null && character.deathYear == null
        ? 'Datas não registradas'
        : 'Nascimento: ${character.birthYear?.toString() ?? '—'}   •   '
            'Falecimento: ${character.deathYear?.toString() ?? '—'}';

    return Material(
      color: ArconteColors.paper,
      shape: RoundedRectangleBorder(
        side: const BorderSide(color: ArconteColors.border),
        borderRadius: BorderRadius.circular(16),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 19, vertical: 19),
          child: Row(children: [
            Container(
              width: 59,
              height: 64,
              decoration: BoxDecoration(
                color: ArconteColors.softPaper,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: ArconteColors.brass.withValues(alpha: .5)),
              ),
              alignment: Alignment.center,
              child: const Icon(Icons.person_outline,
                  size: 29, color: ArconteColors.forest),
            ),
            const SizedBox(width: 18),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(character.fullName,
                      style: ArconteType.cardTitle,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 5),
                  Text(subtitle,
                      style: const TextStyle(
                          fontSize: 13,
                          color: ArconteColors.forestLight,
                          fontWeight: FontWeight.w600),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 8),
                  Text(dates,
                      style: const TextStyle(
                          fontSize: 11.5, color: ArconteColors.secondaryText),
                      softWrap: true),
                ],
              ),
            ),
            const SizedBox(width: 9),
            const Icon(Icons.chevron_right,
                color: ArconteColors.brass, size: 25),
          ]),
        ),
      ),
    );
  }
}

class _InfoPanel extends StatelessWidget {
  const _InfoPanel({
    required this.icon,
    required this.title,
    required this.description,
    this.actionLabel,
    this.onAction,
    this.loading = false,
  });

  final IconData icon;
  final String title;
  final String description;
  final String? actionLabel;
  final VoidCallback? onAction;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 47),
      decoration: BoxDecoration(
        color: ArconteColors.paper,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ArconteColors.border),
      ),
      child: Column(children: [
        if (loading)
          const CircularProgressIndicator(color: ArconteColors.forest)
        else
          Icon(icon, size: 38, color: ArconteColors.brass),
        const SizedBox(height: 18),
        Text(title, style: ArconteType.cardTitle, textAlign: TextAlign.center),
        const SizedBox(height: 10),
        Text(description,
            textAlign: TextAlign.center,
            style: const TextStyle(
                color: ArconteColors.secondaryText, fontSize: 13, height: 1.5)),
        if (actionLabel != null && onAction != null) ...[
          const SizedBox(height: 21),
          FilledButton.tonal(onPressed: onAction, child: Text(actionLabel!)),
        ],
      ]),
    );
  }
}

String _readableError(Object error) {
  if (error is CharacterApiException) return error.message;
  return 'Ocorreu um erro ao carregar os dados. Verifique a conexão com a API.';
}
