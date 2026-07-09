package com.landsense.ai.presentation.capture;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00008\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0005\b\u0007\u0018\u00002\u00020\u0001B\u0017\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0002\u0010\u0006J\u000e\u0010\u000e\u001a\u00020\u000f2\u0006\u0010\u0010\u001a\u00020\u0011J\u0006\u0010\u0012\u001a\u00020\u000fJ\u000e\u0010\u0013\u001a\u00020\u000f2\u0006\u0010\u0014\u001a\u00020\u0011J\u0006\u0010\u0015\u001a\u00020\u000fR\u0014\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010\n\u001a\b\u0012\u0004\u0012\u00020\t0\u000b\u00a2\u0006\b\n\u0000\u001a\u0004\b\f\u0010\r\u00a8\u0006\u0016"}, d2 = {"Lcom/landsense/ai/presentation/capture/CaptureViewModel;", "Landroidx/lifecycle/ViewModel;", "repository", "Lcom/landsense/ai/data/repository/ObservationRepository;", "locationTracker", "Lcom/landsense/ai/util/LocationTracker;", "(Lcom/landsense/ai/data/repository/ObservationRepository;Lcom/landsense/ai/util/LocationTracker;)V", "_state", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/landsense/ai/presentation/capture/CaptureState;", "state", "Lkotlinx/coroutines/flow/StateFlow;", "getState", "()Lkotlinx/coroutines/flow/StateFlow;", "addImage", "", "base64Image", "", "clearError", "setVoiceQuery", "query", "submitObservation", "app_debug"})
@dagger.hilt.android.lifecycle.HiltViewModel()
public final class CaptureViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull()
    private final com.landsense.ai.data.repository.ObservationRepository repository = null;
    @org.jetbrains.annotations.NotNull()
    private final com.landsense.ai.util.LocationTracker locationTracker = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.landsense.ai.presentation.capture.CaptureState> _state = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.landsense.ai.presentation.capture.CaptureState> state = null;
    
    @javax.inject.Inject()
    public CaptureViewModel(@org.jetbrains.annotations.NotNull()
    com.landsense.ai.data.repository.ObservationRepository repository, @org.jetbrains.annotations.NotNull()
    com.landsense.ai.util.LocationTracker locationTracker) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.landsense.ai.presentation.capture.CaptureState> getState() {
        return null;
    }
    
    public final void addImage(@org.jetbrains.annotations.NotNull()
    java.lang.String base64Image) {
    }
    
    public final void setVoiceQuery(@org.jetbrains.annotations.NotNull()
    java.lang.String query) {
    }
    
    public final void clearError() {
    }
    
    public final void submitObservation() {
    }
}