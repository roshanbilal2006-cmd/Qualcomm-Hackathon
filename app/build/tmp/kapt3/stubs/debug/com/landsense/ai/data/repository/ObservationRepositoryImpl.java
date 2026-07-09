package com.landsense.ai.data.repository;

@javax.inject.Singleton()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0007\u0018\u00002\u00020\u0001B\u000f\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u001c\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u0006H\u0096@\u00f8\u0001\u0000\u00f8\u0001\u0001\u00a2\u0006\u0004\b\b\u0010\tJ$\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u000b0\u00062\u0006\u0010\f\u001a\u00020\rH\u0096@\u00f8\u0001\u0000\u00f8\u0001\u0001\u00a2\u0006\u0004\b\u000e\u0010\u000fR\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u0082\u0002\u000b\n\u0002\b!\n\u0005\b\u00a1\u001e0\u0001\u00a8\u0006\u0010"}, d2 = {"Lcom/landsense/ai/data/repository/ObservationRepositoryImpl;", "Lcom/landsense/ai/data/repository/ObservationRepository;", "apiService", "Lcom/landsense/ai/data/network/ApiService;", "(Lcom/landsense/ai/data/network/ApiService;)V", "getHeatmap", "Lkotlin/Result;", "Lcom/landsense/ai/data/network/HeatmapResponse;", "getHeatmap-IoAF18A", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "submitObservation", "Lcom/landsense/ai/data/network/ObservationResponse;", "request", "Lcom/landsense/ai/data/network/ObservationRequest;", "submitObservation-gIAlu-s", "(Lcom/landsense/ai/data/network/ObservationRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public final class ObservationRepositoryImpl implements com.landsense.ai.data.repository.ObservationRepository {
    @org.jetbrains.annotations.NotNull()
    private final com.landsense.ai.data.network.ApiService apiService = null;
    
    @javax.inject.Inject()
    public ObservationRepositoryImpl(@org.jetbrains.annotations.NotNull()
    com.landsense.ai.data.network.ApiService apiService) {
        super();
    }
}