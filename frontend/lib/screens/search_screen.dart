import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/providers/search_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/widgets/search_result_card.dart';

class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final _searchController = TextEditingController();
  DateTimeRange? _dateRange;
  final Set<String> _selectedTags = {};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(tagsProvider.notifier).loadTags();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _triggerSearch() {
    final query = _searchController.text.trim();
    ref.read(searchProvider.notifier).searchDebounced(
      query: query.isNotEmpty ? query : null,
      tags: _selectedTags.isNotEmpty ? _selectedTags.toList() : null,
      dateFrom: _dateRange?.start.toIso8601String().split('T')[0],
      dateTo: _dateRange?.end.toIso8601String().split('T')[0],
    );
  }

  void _toggleTag(String tagLabel) {
    setState(() {
      _selectedTags.contains(tagLabel) ? _selectedTags.remove(tagLabel) : _selectedTags.add(tagLabel);
    });
    _triggerSearch();
  }

  @override
  Widget build(BuildContext context) {
    final searchState = ref.watch(searchProvider);
    final tagsState = ref.watch(tagsProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final hasInput = _searchController.text.isNotEmpty || _selectedTags.isNotEmpty;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('search.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
                const SizedBox(height: 4),
                Text('search.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
            child: Container(
              decoration: ext.cardDecoration,
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    controller: _searchController,
                    style: GoogleFonts.heebo(color: AppColors.textPrimary, fontSize: 14),
                    decoration: InputDecoration(
                      hintText: 'search.hint'.tr(),
                      hintStyle: GoogleFonts.heebo(color: AppColors.textMuted, fontSize: 14),
                      prefixIcon: Icon(Icons.search_rounded, color: AppColors.textMuted, size: 20),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: Icon(Icons.close_rounded, size: 18, color: AppColors.textMuted),
                              onPressed: () {
                                _searchController.clear();
                                setState(() {});
                                _triggerSearch();
                              },
                            )
                          : null,
                      filled: true,
                      fillColor: AppColors.background,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.cardBorder)),
                      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.cardBorder)),
                      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    ),
                    onChanged: (value) {
                      setState(() {});
                      _triggerSearch();
                    },
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Material(
                        color: Colors.transparent,
                        child: InkWell(
                          onTap: () async {
                            final range = await showDateRangePicker(context: context, firstDate: DateTime(2020), lastDate: DateTime.now());
                            if (range != null) {
                              setState(() => _dateRange = range);
                              _triggerSearch();
                            }
                          },
                          borderRadius: BorderRadius.circular(8),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: _dateRange != null ? AppColors.primary.withValues(alpha: 0.1) : AppColors.background,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: _dateRange != null ? AppColors.primary.withValues(alpha: 0.3) : AppColors.cardBorder),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.calendar_today_rounded, size: 14, color: _dateRange != null ? AppColors.primary : AppColors.textMuted),
                                const SizedBox(width: 6),
                                Text(
                                  _dateRange != null
                                      ? '${_dateRange!.start.day}/${_dateRange!.start.month} - ${_dateRange!.end.day}/${_dateRange!.end.month}'
                                      : 'search.date_filter'.tr(),
                                  style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500, color: _dateRange != null ? AppColors.primary : AppColors.textMuted),
                                ),
                                if (_dateRange != null) ...[
                                  const SizedBox(width: 4),
                                  InkWell(
                                    onTap: () {
                                      setState(() => _dateRange = null);
                                      _triggerSearch();
                                    },
                                    child: Icon(Icons.close, size: 14, color: AppColors.primary),
                                  ),
                                ],
                              ],
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      if (_selectedTags.isNotEmpty)
                        Material(
                          color: Colors.transparent,
                          child: InkWell(
                            onTap: () {
                              setState(() => _selectedTags.clear());
                              _triggerSearch();
                            },
                            borderRadius: BorderRadius.circular(8),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(color: AppColors.accent.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.clear_all_rounded, size: 14, color: AppColors.accent),
                                  const SizedBox(width: 4),
                                  Text('search.clear_tags'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500, color: AppColors.accent)),
                                ],
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text('search.tags_label'.tr(), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                  const SizedBox(height: 8),
                  if (tagsState.isLoading)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary)),
                    )
                  else
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: tagsState.tags.map((tag) {
                        final label = tag.tagLabel;
                        final count = tag.count ?? 0;
                        final isSelected = _selectedTags.contains(label);
                        return Material(
                          color: Colors.transparent,
                          child: InkWell(
                            onTap: () => _toggleTag(label),
                            borderRadius: BorderRadius.circular(8),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                              decoration: BoxDecoration(
                                color: isSelected ? AppColors.primary.withValues(alpha: 0.15) : AppColors.background,
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: isSelected ? AppColors.primary : AppColors.cardBorder),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  if (isSelected) ...[
                                    Icon(Icons.check_rounded, size: 14, color: AppColors.primary),
                                    const SizedBox(width: 4),
                                  ],
                                  Text(label, style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500, color: isSelected ? AppColors.primary : AppColors.textSecondary)),
                                  const SizedBox(width: 4),
                                  Text('($count)', style: GoogleFonts.heebo(fontSize: 10, color: AppColors.textMuted)),
                                ],
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (hasInput)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Row(
                children: [
                  if (searchState.isLoading)
                    Padding(
                      padding: const EdgeInsets.only(left: 8),
                      child: SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary)),
                    ),
                  const SizedBox(width: 8),
                  Text(
                    searchState.isLoading ? 'common.searching'.tr() : 'search.results_count'.tr(namedArgs: {'count': searchState.total.toString()}),
                    style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 4),
          Expanded(
            child: !hasInput
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.search_rounded, size: 56, color: AppColors.textMuted.withValues(alpha: 0.3)),
                        const SizedBox(height: 16),
                        Text('search.empty_hint'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                        const SizedBox(height: 6),
                        Text('search.empty_subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
                      ],
                    ),
                  )
                : searchState.error != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.error_outline_rounded, size: 48, color: AppColors.accent.withValues(alpha: 0.6)),
                            const SizedBox(height: 16),
                            Text('search.error'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                          ],
                        ),
                      )
                    : searchState.results.isEmpty && !searchState.isLoading
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.search_off_rounded, size: 48, color: AppColors.textMuted.withValues(alpha: 0.4)),
                                const SizedBox(height: 16),
                                Text('search.no_results'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                                const SizedBox(height: 6),
                                Text('search.no_results_hint'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
                              ],
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 24),
                            itemCount: searchState.results.length,
                            itemBuilder: (context, index) => SearchResultCard(result: searchState.results[index]),
                          ),
          ),
        ],
      ),
    );
  }
}
