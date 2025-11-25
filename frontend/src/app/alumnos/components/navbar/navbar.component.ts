import { AlumnoStateService } from '@/alumnos/services/alumno-state.service';
import { AuthService } from '@/auth/services/auth.service';
import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';


@Component({
  selector: 'navbar',
  templateUrl: './navbar.component.html',
  imports: [RouterLink]
})
export class NavbarComponent {
  router = inject(Router);
  alumnoStateService = inject(AlumnoStateService)
  auth = inject(AuthService);

  mobileMenuOpen = signal<boolean>(false);

  // Alterna el estado del menú móvil (abierto/cerrado).
  toggleMobileMenu(): void {
    this.mobileMenuOpen.set(!this.mobileMenuOpen());
  }

  // Cierra el menú móvil.
  closeMobileMenu(): void {
    this.mobileMenuOpen.set(false);
  }

  // Navega a la página del alumno.
  goToAlumnoPage(): void {
    const alumnoId = this.alumnoStateService.getId();
    if (alumnoId != null){
      this.router.navigate([`alumno/${alumnoId}`]);
    }
    else{
      this.router.navigate(['/alumno']);
    }
  }

  // Navega a la página de login de administradores.
  goToAdminLogin(): void {
    // ejemplo: ruta dedicada a login de administradores
    this.router.navigate(['/admin/login']);
  }

}
