import os
from dotenv import load_dotenv

load_dotenv()

def check_stripe_config():
    print("🔍 Verificando configuração do Stripe...")
    
    stripe_secret = os.environ.get('STRIPE_SECRET_KEY')
    stripe_public = os.environ.get('STRIPE_PUBLIC_KEY')
    stripe_webhook = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    prices = {
        'assinatura': os.environ.get('STRIPE_PRICE_ASSINATURA'),
        'vida_1': os.environ.get('STRIPE_PRICE_VIDA_1'),
        'vida_3': os.environ.get('STRIPE_PRICE_VIDA_3'),
        'vida_5': os.environ.get('STRIPE_PRICE_VIDA_5'),
    }
    
    print(f"✅ STRIPE_SECRET_KEY: {'***' + stripe_secret[-8:] if stripe_secret else '❌ NÃO CONFIGURADO'}")
    print(f"✅ STRIPE_PUBLIC_KEY: {'***' + stripe_public[-8:] if stripe_public else '❌ NÃO CONFIGURADO'}")
    print(f"✅ STRIPE_WEBHOOK_SECRET: {'***' + stripe_webhook[-8:] if stripe_webhook else '❌ NÃO CONFIGURADO'}")
    
    print("\n🔍 Preços configurados:")
    for price_type, price_id in prices.items():
        status = '✅' if price_id else '❌'
        print(f"   {status} {price_type}: {price_id or 'NÃO CONFIGURADO'}")

if __name__ == '__main__':
    check_stripe_config()