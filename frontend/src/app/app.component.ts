import { Component, inject } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { NavbarComponent } from "./alumnos/components/navbar/navbar.component";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NavbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'tfg-front';
  router = inject(Router);

  showNavbar(): boolean {
    const currentRoute = this.router.url;
    return currentRoute !== '/admin';
  }
}
