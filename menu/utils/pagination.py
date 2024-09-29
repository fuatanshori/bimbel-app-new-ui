from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

def pagination_queryset(request,queryset,amount_perpage=2):
    page = request.GET.get('page')
    paginator = Paginator(queryset,amount_perpage)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        page=1
        queryset = paginator.page(page)
    except EmptyPage:
        page= paginator.num_pages
        queryset = paginator.page(page)
    
    left_index = (int(page)-1)
    if left_index < 1:
        left_index = 1
    
    right_index = (int(page)+2)
    if right_index > paginator.num_pages:
        right_index = paginator.num_pages + 1
    custom_range =range(left_index,right_index)
    return custom_range,queryset