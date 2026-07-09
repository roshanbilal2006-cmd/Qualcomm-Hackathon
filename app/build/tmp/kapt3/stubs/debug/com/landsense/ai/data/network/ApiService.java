package com.landsense.ai.data.network;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\bf\u0018\u00002\u00020\u0001J\u000e\u0010\u0002\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0018\u0010\u0005\u001a\u00020\u00062\b\b\u0001\u0010\u0007\u001a\u00020\bH\u00a7@\u00a2\u0006\u0002\u0010\t\u00a8\u0006\n"}, d2 = {"Lcom/landsense/ai/data/network/ApiService;", "", "getHeatmap", "Lcom/landsense/ai/data/network/HeatmapResponse;", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "submitObservation", "Lcom/landsense/ai/data/network/ObservationResponse;", "request", "Lcom/landsense/ai/data/network/ObservationRequest;", "(Lcom/landsense/ai/data/network/ObservationRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public abstract interface ApiService {
    
    @retrofit2.http.POST(value = "observation")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object submitObservation(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.landsense.ai.data.network.ObservationRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.landsense.ai.data.network.ObservationResponse> $completion);
    
    @retrofit2.http.GET(value = "heatmap")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getHeatmap(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.landsense.ai.data.network.HeatmapResponse> $completion);
}