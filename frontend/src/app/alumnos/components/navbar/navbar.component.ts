import { AlumnoStateService } from '@/alumnos/services/alumno-state.service';
import { AuthService } from '@/auth/services/auth.service';
import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { RouterLink } from "../../../../../node_modules/@angular/router/router_module.d-BivBj8FC";

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

  toggleMobileMenu(): void {
    this.mobileMenuOpen.set(!this.mobileMenuOpen());
  }

  closeMobileMenu(): void {
    this.mobileMenuOpen.set(false);
  }

  goToAlumnoPage(): void {
    const alumnoId = this.alumnoStateService.getId();
    console.log("Navegando a la página del alumno con ID:", alumnoId);
    if (alumnoId != null){
      this.router.navigate([`alumno/${alumnoId}`]);
    }
    else{
      this.router.navigate(['/alumno']);
    }
  }

  goToAdminLogin(): void {
    // ejemplo: ruta dedicada a login de administradores
    this.router.navigate(['/admin/login']);
  }

}
