// Directly from: https://gitlab.com/studieverenigingvia/viaduct/-/blob/master/frontend/utils/VuePaginatedAnt.ts?ref_type=heads
import { ref, reactive, computed, Ref, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { notification } from "ant-design-vue";

function debounce(fn, delay) {
  let timeout: number;
  return function (...args) {
    if (timeout !== undefined) {
      clearTimeout(timeout);
    }
    timeout = window.setTimeout(() => fn.apply(this, args), delay);
  };
}

export type VuePaginatedAntDataFunction<T> = (
  search: string,
  sort: string,
  page: number,
  pageSize: number,
) => Promise<{
  data: T[];
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
  };
}>;

export function VuePaginatedAntComposable<T>(
  dataFunction: VuePaginatedAntDataFunction<T>,
) {
  const loadingRef = ref(true);
  const dataRef = ref<T[]>([]) as Ref<T[]>;
  const paginationRef = reactive({ current: 1, pageSize: 10, total: 0 });

  const route = useRoute();
  const router = useRouter();

  // The actual search value is stored in a ref, so that we can instantly update the search value
  // If we would only use the query (as with sort/page), the input field would be updated with a delay
  // This is because the router.replace function is "slow".
  const actualSearch = ref((route.query.search as string) ?? "");
  const search = computed({
    get() {
      return actualSearch.value;
    },
    set(search) {
      paginationRef.current = 1;
      page.value = 1;
      actualSearch.value = search;
      debouncedRefreshListView();
      nextTick(() => {
        router.replace({
          query: {
            ...route.query,
            search,
            page: paginationRef.current.toString(),
          },
        });
      });
    },
  });

  const actualSort = ref((route.query.sort as string) ?? "");
  const sort = computed({
    get() {
      return actualSort.value;
    },
    set(sort) {
      console.log("Replacing sort", sort);
      actualSort.value = sort;
      paginationRef.current = 1;
      debouncedRefreshListView();
      nextTick(() => {
        router.replace({ query: { ...route.query, sort } });
      });
    },
  });

  const actualPage = ref(parseInt(route.query.page as string) || 1);
  const page = computed({
    get() {
      return actualPage.value;
    },
    set(page) {
      actualPage.value = page;
      paginationRef.current = page;
      debouncedRefreshListView();

      nextTick(() => {
        router.replace({
          query: { ...route.query, page: page.toString() },
        });
      });
    },
  });

  const actualPageSize = ref(parseInt(route.query.pageSize as string) || 10);
  const pageSize = computed({
    get() {
      return actualPageSize.value;
    },
    set(pageSize) {
      actualPageSize.value = pageSize;
      paginationRef.pageSize = pageSize;
      debouncedRefreshListView();

      nextTick(() => {
        router.replace({
          query: { ...route.query, pageSize: pageSize.toString() },
        });
      });
    },
  });

  const refreshListView = async () => {
    loadingRef.value = true;
    try {
      const { data, pagination } = await dataFunction(
        search.value,
        sort.value,
        page.value,
        paginationRef.pageSize,
      );
      if (pagination) {
        paginationRef.current = pagination.current;
        paginationRef.pageSize = pagination.pageSize;
        paginationRef.total = pagination.total;
      }
      dataRef.value = data;
    } catch (e) {
      notification.error({
        message: "Something went wrong",
        description: "Please try again later",
      });
      console.error(e);
    } finally {
      loadingRef.value = false;
    }
  };

  const debouncedRefreshListView = debounce(refreshListView, 300);

  const handleTableChange = (pagination, filters, sorter) => {
    if (sorter["columnKey"]) {
      let newSort = sorter["columnKey"];
      if (sorter["order"] === "descend") {
        newSort = `-${newSort}`;
      }
      sort.value = newSort;
    }
    pagination.value = pagination;
    page.value = pagination.current;
    debouncedRefreshListView();
  };

  const pageSwitch = async (pageNew: number) => {
    page.value = pageNew;
  };

  refreshListView();

  return {
    loading: loadingRef,
    pagination: paginationRef,
    data: dataRef,
    refreshListView,
    debouncedRefreshListView,
    handleTableChange,
    sort,
    search,
    page,
    pageSize,
    pageSwitch,
  };
}
