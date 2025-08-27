import { AuthService } from '@/auth/services/auth.service';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-page',
  imports: [ReactiveFormsModule],
  templateUrl: './admin-login-page.component.html',
})
export class AdminLoginPageComponent {

  authService = inject(AuthService)
  router = inject(Router)

  fb = inject(FormBuilder);
  hasError = signal(false)
  isPosting = signal(false)

  loginForm = this.fb.group({
    user: ['', [Validators.required]],
    password: ['', [Validators.required]],
  })
  //TODO: Arreglar el HTML de login
  onSubmit(){
    if(this.loginForm.invalid){
      this.hasError.set(true)
      setTimeout(() =>  {
        this.hasError.set(false)
      },2000)
      return
    }

    const {user = '', password = ''} = this.loginForm.value
    this.authService.login(user!, password!)
    .subscribe((response) =>{
      if(response === "Usuario autorizado"){
        this.router.navigateByUrl('/admin')
        return;
      }
      this.hasError.set(true)
      setTimeout(() =>  {
        this.hasError.set(false)
      },2000)
    })
  }
}