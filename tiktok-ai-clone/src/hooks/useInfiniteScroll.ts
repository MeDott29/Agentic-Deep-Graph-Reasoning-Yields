import { useState, useEffect, useCallback, RefObject } from 'react';

interface UseInfiniteScrollOptions {
  loading: boolean;
  hasMore: boolean;
  onLoadMore: () => void;
  rootMargin?: string;
  threshold?: number;
  targetRef?: RefObject<HTMLElement>;
}

const useInfiniteScroll = ({
  loading,
  hasMore,
  onLoadMore,
  rootMargin = '0px',
  threshold = 0.1,
  targetRef,
}: UseInfiniteScrollOptions) => {
  const [observer, setObserver] = useState<IntersectionObserver | null>(null);

  // Callback for intersection observer
  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      // If the element is visible and we're not currently loading and there's more to load
      if (entry.isIntersecting && !loading && hasMore) {
        onLoadMore();
      }
    },
    [loading, hasMore, onLoadMore]
  );

  // Set up the intersection observer
  useEffect(() => {
    // If we already have an observer, disconnect it
    if (observer) {
      observer.disconnect();
    }

    // Create a new observer
    const newObserver = new IntersectionObserver(handleObserver, {
      rootMargin,
      threshold,
    });

    setObserver(newObserver);

    // If we have a target element, observe it
    if (targetRef && targetRef.current) {
      newObserver.observe(targetRef.current);
    }

    // Clean up the observer when the component unmounts
    return () => {
      if (newObserver) {
        newObserver.disconnect();
      }
    };
  }, [handleObserver, rootMargin, threshold, targetRef]);

  return { observer };
};

export default useInfiniteScroll; 