import React, { useRef, useEffect } from 'react';

// Svg Icons
const OpenAI_Logo = () => (
    <svg viewBox="0 0 24 24" className="w-5 h-5 fill-openai" xmlns="http://www.w3.org/2000/svg"><path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.0462 6.0462 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a1.8733 1.8733 0 0 0 2.763-.9199V16.82a4.524 4.524 0 0 1-5.698 5.6092zm-6.9584-2.3444a4.4755 4.4755 0 0 1-.5363-3.0537l.142-.0804 4.7783-2.7582a.7951.7951 0 0 0 .3927-.6813v-6.7369l2 .32v11.5312a4.49 4.49 0 0 1-3.2359 1.4593zm-4.6321-7.0142a4.5145 4.5145 0 0 1 1.764-5.2281l4.7783-2.7582a.7951.7951 0 0 0 .3927-.6813V2l3.41 1.96 4.71 2.71a4.49 4.49 0 0 1-3.2359 1.4593v-6.7369l-2 .32-4.72 2.72zm15.6125 0a4.5145 4.5145 0 0 1-1.764 5.2281l-4.7783 2.7582a.7951.7951 0 0 0-.3927.6813v.81l-2.02-1.1686a1.8733 1.8733 0 0 0-2.763.9199v-6.7369l4.72-2.72 4.71-2.71a4.49 4.49 0 0 1 3.2359-1.4593zm-3.0906-8.7735a4.4755 4.4755 0 0 1 2.8764 1.0408l-.1419.0804-4.7783 2.7582a.7951.7951 0 0 0-.3927.6813v6.7369l-2.02-1.1686a1.8733 1.8733 0 0 0-2.763.9199V6.03a4.524 4.524 0 0 1 5.698-5.6092z" /></svg>
);

const Anthropic_Logo = () => (
    <svg viewBox="0 0 24 24" className="w-5 h-5 fill-anthropic" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="currentColor" />
        <path d="M12.9 5.05l5.12 12.02h-2.58l-1.07-2.65H9.63l-1.07 2.65H5.97L11.1 5.05h1.8Zm-1.85 7.64l-1.37-3.41-1.37 3.41h2.74Z" fill="black" />
    </svg>
);

const DeepMind_Logo = () => (
    <svg viewBox="0 0 24 24" className="w-5 h-5 fill-deepmind" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" /></svg>
);

const Meta_Logo = () => (
    <svg viewBox="0 0 24 24" className="w-5 h-5 fill-meta" xmlns="http://www.w3.org/2000/svg"><path d="M12.0003 5.48003C7.22158 5.48003 2.9248 10.1558 2.9248 12.0309C2.9248 14.3311 7.22158 18.2573 12.0003 18.2573C16.8906 18.2573 21.0752 14.6192 21.0752 12.0309C21.0752 9.07409 16.8906 5.48003 12.0003 5.48003ZM12.0003 16.2731C9.65839 16.2731 7.76019 14.3749 7.76019 12.033C7.76019 9.69114 9.65839 7.79289 12.0003 7.79289C14.3418 7.79289 16.2404 9.69114 16.2404 12.033C16.2404 14.3749 14.3418 16.2731 12.0003 16.2731Z" /></svg>
);

const ICONS = {
    'OpenAI': OpenAI_Logo,
    'Anthropic': Anthropic_Logo,
    'Google DeepMind': DeepMind_Logo,
    'Meta AI': Meta_Logo,
};

const DEFAULT_ICON = () => <div className="w-5 h-5 bg-gray-400 rounded-full"></div>;

export default function ArticleStream({ articles, loading, selectedTrend, loadMore, hasMore }) {
    const observerTarget = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            entries => {
                if (entries[0].isIntersecting && hasMore) {
                    loadMore();
                }
            },
            { threshold: 0.1 }
        );

        if (observerTarget.current) {
            observer.observe(observerTarget.current);
        }

        return () => {
            if (observerTarget.current) {
                observer.unobserve(observerTarget.current);
            }
        };
    }, [hasMore, loadMore]);

    if (loading && (!articles || articles.length === 0)) {
        return (
            <div className="space-y-8 animate-pulse">
                {[1, 2, 3].map(i => (
                    <div key={i} className="flex gap-4">
                        <div className="w-1 bg-gray-200 rounded-full h-24"></div>
                        <div className="flex-1 space-y-3 py-2">
                            <div className="h-5 bg-gray-200 rounded w-1/4"></div>
                            <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (!articles || articles.length === 0) {
        return (
            <div className="text-center py-20 bg-white border border-dashed border-gray-200 rounded-lg">
                <p className="text-gray-400 font-sans italic text-lg">
                    No news found for this specific timeframe.
                </p>
                <p className="text-gray-300 text-sm mt-2">Try checking "7 Days" or "30 Days".</p>
            </div>
        );
    }

    return (
        <div className="space-y-12 transition-all duration-500">
            {articles.map((article, index) => {
                const Icon = ICONS[article.source] || DEFAULT_ICON;
                const delay = index * 50;

                // Filtering Logic
                const isDimmed = selectedTrend && !selectedTrend.article_ids?.includes(article.id);

                return (
                    <div
                        key={article.id}
                        className={`block group transition-all duration-500 ${isDimmed ? 'opacity-20 grayscale pointer-events-none' : 'opacity-100'}`}
                        style={{
                            animation: !isDimmed ? `fadeInUp 0.5s ease-out ${delay}ms forwards` : 'none'
                        }}
                    >
                        <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block mb-3"
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <Icon />
                                <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">
                                    {article.source}
                                </span>
                                <span className="text-xs text-gray-300">•</span>
                                <span className="text-xs text-gray-400">
                                    {new Date(article.published).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                                </span>
                            </div>

                            <h3 className="text-2xl font-serif font-medium text-text-main group-hover:underline decoration-2 decoration-gray-200 decoration-offset-4 leading-tight mb-2">
                                {article.title}
                            </h3>
                        </a>

                        {/* One-Line Summary */}
                        <p className="text-gray-600 font-sans text-sm leading-relaxed max-w-2xl border-l-2 border-gray-100 pl-4">
                            {article.summary || "Summary not available yet."}
                        </p>
                    </div>
                );
            })}

            {/* Sentinel for Infinite Scroll */}
            {hasMore && (
                <div ref={observerTarget} className="py-12 text-center opacity-50">
                    <div className="inline-block h-6 w-6 animate-spin rounded-full border-4 border-solid border-gray-400 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" role="status">
                        <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
                    </div>
                </div>
            )}

            {!hasMore && articles.length > 20 && (
                <div className="py-12 text-center text-gray-300 text-xs font-sans uppercase tracking-widest border-t border-gray-100 mt-12">
                    End of Stream
                </div>
            )}

            <style>{`
          @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
        `}</style>
        </div>
    );
}
