import { AlumnoStateService } from '@/alumnos/services/alumno-state.service';
import { AuthService } from '@/auth/services/auth.service';
import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';

@Component({
  selector: 'navbar',
  templateUrl: './navbar.component.html'
})
export class NavbarComponent implements OnInit, OnDestroy {
  router = inject(Router);
  alumnoStateService = inject(AlumnoStateService)
  auth = inject(AuthService);

  mobileMenuOpen = signal<boolean>(false);
  isAdmin = signal<boolean>(true);

  private sub = new Subscription();

  ngOnInit(): void {
    // suponemos que AuthService expone isAdmin$ (BehaviorSubject/Observable<boolean>)
    // this.sub.add(
    //   this.auth.isAdmin$.subscribe((v) => {
    //     this.isAdmin.set(!!v);
    //   })
    // );
  }

  toggleMobileMenu(): void {
    this.mobileMenuOpen.set(!this.mobileMenuOpen());
  }

  closeMobileMenu(): void {
    this.mobileMenuOpen.set(false);
  }

  goToAlumnoPage(): void {
    const alumnoId = this.alumnoStateService.getId();
    if (alumnoId != null){
      this.router.navigate(['/alumno', alumnoId]);
    }
    this.router.navigate(['/alumno']);
  }

  goToAdminLogin(): void {
    // ejemplo: ruta dedicada a login de administradores
    this.router.navigate(['/admin/login']);
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }
}
