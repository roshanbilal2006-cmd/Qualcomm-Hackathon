package com.landsense.ai.presentation.capture;

import com.landsense.ai.data.repository.ObservationRepository;
import com.landsense.ai.util.LocationTracker;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava",
    "cast"
})
public final class CaptureViewModel_Factory implements Factory<CaptureViewModel> {
  private final Provider<ObservationRepository> repositoryProvider;

  private final Provider<LocationTracker> locationTrackerProvider;

  public CaptureViewModel_Factory(Provider<ObservationRepository> repositoryProvider,
      Provider<LocationTracker> locationTrackerProvider) {
    this.repositoryProvider = repositoryProvider;
    this.locationTrackerProvider = locationTrackerProvider;
  }

  @Override
  public CaptureViewModel get() {
    return newInstance(repositoryProvider.get(), locationTrackerProvider.get());
  }

  public static CaptureViewModel_Factory create(Provider<ObservationRepository> repositoryProvider,
      Provider<LocationTracker> locationTrackerProvider) {
    return new CaptureViewModel_Factory(repositoryProvider, locationTrackerProvider);
  }

  public static CaptureViewModel newInstance(ObservationRepository repository,
      LocationTracker locationTracker) {
    return new CaptureViewModel(repository, locationTracker);
  }
}
