from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def pagination_queryset(request, queryset, amount_perpage=2):
    # Get the current page number from the query parameters
    page = request.GET.get('page', 1)  # Default to the first page if not provided
    paginator = Paginator(queryset, amount_perpage)
    
    try:
        # Get the objects for the current page
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page
        queryset = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        queryset = paginator.page(paginator.num_pages)
    
    # Calculate the range for pagination display
    left_index = max(1, int(page) - 1)  # Ensure left index is at least 1
    right_index = min(int(page) + 2, paginator.num_pages + 1)  # Ensure right index does not exceed total pages
    custom_range = range(left_index, right_index)

    return custom_range, queryset
