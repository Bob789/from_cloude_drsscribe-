import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/models/search_result_model.dart';
import 'package:medscribe_ai/models/tag_model.dart';

class SearchState {
  final bool isLoading;
  final List<SearchResultModel> results;
  final int total;
  final String? error;

  const SearchState({this.isLoading = false, this.results = const [], this.total = 0, this.error});
}

class SearchNotifier extends StateNotifier<SearchState> {
  final _api = api;
  Timer? _debounce;

  SearchNotifier() : super(const SearchState());

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  void searchDebounced({
    String? query,
    List<String>? tags,
    String? dateFrom,
    String? dateTo,
  }) {
    _debounce?.cancel();
    final q = query?.trim();
    if ((q == null || q.isEmpty) && (tags == null || tags.isEmpty)) {
      state = const SearchState();
      return;
    }
    _debounce = Timer(const Duration(milliseconds: 250), () {
      search(query: q, tags: tags, dateFrom: dateFrom, dateTo: dateTo);
    });
  }

  Future<void> search({
    String? query,
    List<String>? tags,
    String? dateFrom,
    String? dateTo,
    int page = 1,
  }) async {
    if ((query == null || query.isEmpty) && (tags == null || tags.isEmpty)) {
      state = const SearchState();
      return;
    }

    state = SearchState(isLoading: true, results: state.results, total: state.total);
    try {
      final params = <String, dynamic>{'page': page};
      if (query != null && query.isNotEmpty) params['q'] = query;
      if (tags != null && tags.isNotEmpty) params['tags'] = tags.join(',');
      if (dateFrom != null) params['date_from'] = dateFrom;
      if (dateTo != null) params['date_to'] = dateTo;

      final response = await _api.get('/search', queryParameters: params);
      final hits = (response.data['hits'] as List).map((h) => SearchResultModel.fromJson(h)).toList();
      state = SearchState(results: hits, total: (response.data['total'] as num?)?.toInt() ?? 0);
    } catch (e) {
      state = SearchState(error: e.toString());
    }
  }
}

final searchProvider = StateNotifierProvider<SearchNotifier, SearchState>((ref) => SearchNotifier());

class TagsState {
  final bool isLoading;
  final List<TagModel> tags;

  const TagsState({this.isLoading = false, this.tags = const []});
}

class TagsNotifier extends StateNotifier<TagsState> {
  final _api = api;

  TagsNotifier() : super(const TagsState());

  Future<void> loadTags() async {
    state = TagsState(isLoading: true, tags: state.tags);
    try {
      final response = await _api.get('/tags');
      final tags = (response.data['tags'] as List).map((t) => TagModel.fromJson(t)).toList();
      state = TagsState(tags: tags);
    } catch (e) {
      state = const TagsState();
    }
  }

  Future<void> createTag({
    required String entityType,
    required String entityId,
    required String tagType,
    required String tagLabel,
    String? tagCode,
  }) async {
    try {
      await _api.post('/tags', data: {
        'entity_type': entityType,
        'entity_id': entityId,
        'tag_type': tagType,
        'tag_label': tagLabel,
        'tag_code': tagCode,
      });
      await loadTags();
    } catch (_) {}
  }
}

final tagsProvider = StateNotifierProvider<TagsNotifier, TagsState>((ref) => TagsNotifier());
