from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from novels.models import Novel, Tag, novel
from novels.models.reading_favorite import Favorite
from novels.services import NovelService
from novels.forms import NovelForm
from django.core.paginator import Paginator
from interactions.services import ReviewService
from constants import (
    ApprovalStatus, ProgressStatus, DATE_FORMAT_DMY, MAX_CHAPTER_LIST,
    MAX_CHAPTER_LIST_PLUS, DATE_FORMAT_DMYHI, SEARCH_RESULTS_LIMIT,
    MAX_TRUNCATED_REJECTED_REASON_LENGTH, PAGINATION_PAGE_RANGE,
    SUMMARY_TRUNCATE_WORDS, DEFAULT_RATING_AVERAGE, MIN_RATE, MAX_RATE,
    MAX_LENGTH_REVIEW_CONTENT, NOVEL_PER_PAGE, DEFAULT_PAGE_NUMBER
)
from common.decorators import require_active_novel
from novels.services.novel_service import FavoriteService, get_liked_novels

@require_active_novel
def novel_detail(request, novel_slug):
    """Novel detail page using service"""
    novel_data = NovelService.get_novel_detail(novel_slug, request.user)

    if not novel_data:
        return redirect("novels:home")
    novel = get_object_or_404(Novel, slug=novel_slug)
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, novel=novel).exists()
    
    
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = ReviewService.has_user_reviewed_novel(request.user, novel_data['novel'])

    context = {
        'is_owner': novel_data['is_owner'],
        'novel_slug': novel_slug,
        'novel': novel_data['novel'],
        "is_favorited": is_favorited,
        'tags': novel_data['tags'],
        'volumes': novel_data['volumes'],
        'can_add_chapter': novel_data['can_add_chapter'],
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'MAX_CHAPTER_LIST': MAX_CHAPTER_LIST,
        'MAX_CHAPTER_LIST_PLUS': MAX_CHAPTER_LIST_PLUS,
        'rating_stars': range(MIN_RATE + 1, MAX_RATE + 1),
        'user_has_reviewed': user_has_reviewed,
        'MAX_LENGTH_REVIEW_CONTENT': MAX_LENGTH_REVIEW_CONTENT,
    }
    return render(request, "novels/pages/novel_detail.html", context)

class NovelCreateView(LoginRequiredMixin, CreateView):
    """Create new novel view"""
    model = Novel
    form_class = NovelForm
    template_name = "novels/pages/novel_form.html"
    success_url = reverse_lazy("novels:home")
    login_url = reverse_lazy("accounts:login")
    permission_denied_message = _("Bạn cần đăng nhập để tạo tiểu thuyết mới.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tạo tiểu thuyết mới")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        save_as_draft = self.request.POST.get("save_as_draft", False)

        if save_as_draft:
            form.instance.approval_status = ApprovalStatus.DRAFT.value
        else:
            form.instance.approval_status = ApprovalStatus.PENDING.value

        upload_anonymously = form.cleaned_data.get("upload_anonymously", False)
        form.instance.is_anonymous = upload_anonymously
        form.instance.created_by = self.request.user if self.request.user.is_authenticated else None

        response = super().form_valid(form)

        # Handle ManyToMany tags relationship
        tags = form.cleaned_data.get("tags")
        if tags:
            self.object.tags.set(tags)

        return response

class MyNovelsView(LoginRequiredMixin, ListView):
    """User's novels management page using service"""
    template_name = "novels/pages/my_novels.html"
    context_object_name = "page_obj"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        status_filter = self.request.GET.get('status')
        page = self.request.GET.get('page', DEFAULT_PAGE_NUMBER)
        return NovelService.get_user_novels_paginated(
            user=self.request.user,
            status_filter=status_filter,
            page=page
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tiểu thuyết của tôi")
        context["DATE_FORMAT_DMY"] = DATE_FORMAT_DMY
        context["DATE_FORMAT_DMYHI"] = DATE_FORMAT_DMYHI
        
        # Get statistics using service
        stats = NovelService.get_user_novels_with_stats(self.request.user)
        context.update(stats)
        
        # Add status constants
        context.update({
            "DRAFT": ApprovalStatus.DRAFT.value,
            "PENDING": ApprovalStatus.PENDING.value,
            "APPROVED": ApprovalStatus.APPROVED.value,
            "REJECTED": ApprovalStatus.REJECTED.value,
            "MAX_TRUNCATED_REJECTED_REASON_LENGTH": MAX_TRUNCATED_REJECTED_REASON_LENGTH,
            "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE,
            "current_filter": self.request.GET.get('status', 'all')
        })
        
        # Calculate pagination range
        if 'page_obj' in context and context['page_obj']:
            current_page = context['page_obj'].number
            context["pagination_start"] = current_page - PAGINATION_PAGE_RANGE
            context["pagination_end"] = current_page + PAGINATION_PAGE_RANGE
        
        return context

def novel_upload_rules(request):
    """Static page showing novel upload rules"""
    return render(request, 'novels/pages/novel_upload_rule.html')

def search_novels(request):
    """Search novels using service"""
    query = request.GET.get('q', '').strip()
    tags_selected = request.GET.getlist('tags')
    author = request.GET.get('author', '').strip()
    artist = request.GET.get('artist', '').strip()
    status = request.GET.get('status', '').strip()
    sort = request.GET.get('sort', '').strip()
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)

    novels = Novel.objects.filter(
    approval_status=ApprovalStatus.APPROVED.value,
    deleted_at__isnull=True
    )

    if query:
        novels = NovelService.search_novels(query)

    if tags_selected:
        for tag_slug in tags_selected:
            novels = novels.filter(tags__slug=tag_slug)
    if author:
        novels = novels.filter(author__name__icontains=author)
    if artist:
        novels = novels.filter(artist__name__icontains=artist)
    if status:
        novels = novels.filter(progress_status=status)
    if query:
        if sort == 'updated':
            novels = novels.order_by('-updated_at')
        elif sort == 'rating':
            novels = novels.order_by('-rating_avg')
    else:
        novels = novels.order_by('-view_count')

    novels = novels.select_related('author', 'artist').prefetch_related('tags').distinct()

    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(novels, NOVEL_PER_PAGE)
    page_obj = paginator.get_page(page)

    for novel in page_obj:
        novel.tag_list = list(novel.tags.all())
        novel.rating_display = getattr(novel, 'rating_avg', DEFAULT_RATING_AVERAGE) if hasattr(novel, 'rating_avg') and novel.rating_avg > 0 else DEFAULT_RATING_AVERAGE

    all_tags = Tag.objects.all().order_by('name')

    # Calculate pagination range
    pagination_start = None
    pagination_end = None
    if page_obj:
        current_page = page_obj.number
        pagination_start = current_page - PAGINATION_PAGE_RANGE
        pagination_end = current_page + PAGINATION_PAGE_RANGE

    context = {
        'novels': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'tags_selected': tags_selected,
        'filter_author': author,
        'filter_artist': artist,
        'filter_status': status,
        'all_tags': all_tags,
        'filter_sort': sort,
        'total_results': paginator.count if page_obj else 0,
        'SUMMARY_TRUNCATE_WORDS': SUMMARY_TRUNCATE_WORDS,
        'DEFAULT_RATING_AVERAGE': DEFAULT_RATING_AVERAGE,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
        'pagination_start': pagination_start,
        'pagination_end': pagination_end,
    }
    
    return render(request, 'novels/pages/search_results.html', context)

@login_required
def toggle_like(request, novel_slug):
    novel = get_object_or_404(Novel, slug=novel_slug)
    liked = FavoriteService.toggle_like(request.user, novel)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "count": novel.favorites.count()})
    return redirect('novels:novel_detail', novel_slug=novel.slug)

@login_required
def liked_novels(request):
    page_number = request.GET.get("page")
    page_obj = get_liked_novels(request.user, page_number)

    return render(request, "novels/pages/like_novels.html", {
        "page_obj": page_obj,
    })

