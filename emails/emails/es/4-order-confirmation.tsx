/**
 * 4. Confirmación de Compra
 * Estilo: Minimalista elegante inspirado en Tidal
 */

import {
  Body,
  Column,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Preview,
  Row,
  Section,
  Text,
} from '@react-email/components';

interface OrderItem {
  name: string;
  quantity: number;
}

interface OrderConfirmationEmailProps {
  user_name?: string;
  order_number?: string;
  total?: number;
  items?: OrderItem[];
}

export const OrderConfirmationEmail = ({
  user_name = 'Usuario',
  order_number = 'ORD-12345',
  total = 120500,
  items = [
    { name: 'Producto de ejemplo', quantity: 1 },
    { name: 'Otro producto', quantity: 2 },
  ],
}: OrderConfirmationEmailProps) => {

  return (
    <Html>
      <Head />
      <Preview>Tu orden {order_number} ha sido confirmada</Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Logo */}
          <Section style={logoSection}>
            <Img
              src="https://crushme.com.co/static/frontend/BUY.png"
              width="120"
              height="120"
              alt="CrushMe"
              style={logo}
            />
          </Section>

          {/* Título */}
          <Heading style={heading}>¡Gracias por tu compra!</Heading>

          {/* Saludo */}
          <Text style={text}>Hola {user_name},</Text>

          {/* Mensaje principal */}
          <Text style={text}>
            Tu orden ha sido confirmada y está siendo procesada. Te notificaremos cuando sea enviada.
          </Text>

          {/* Información de la orden */}
          <Section style={orderInfoBox}>
            <Text style={orderLabel}>Número de orden</Text>
            <Text style={orderValue}>{order_number}</Text>
          </Section>

          {/* Productos */}
          <Section style={productsSection}>
            <Text style={sectionTitle}>Productos</Text>
            {items.map((item, index) => (
              <Row key={index} style={productRow}>
                <Column>
                  <Text style={productName}>{item.name}</Text>
                </Column>
                <Column align="right">
                  <Text style={productQuantity}>x{item.quantity}</Text>
                </Column>
              </Row>
            ))}
          </Section>

          <Hr style={divider} />

          {/* Total */}
          <Section style={totalsSection}>
            <Row style={totalRow}>
              <Column>
                <Text style={totalLabelBold}>Total</Text>
              </Column>
              <Column align="right">
                <Text style={totalValueBold}>${total.toLocaleString('es-CO')}</Text>
              </Column>
            </Row>
          </Section>

          {/* Footer */}
          <Text style={footer}>
            Si tienes alguna pregunta sobre tu orden, no dudes en contactarnos.
          </Text>

          <Text style={footerSmall}>
            CrushMe · Medellín, Colombia
          </Text>
        </Container>
      </Body>
    </Html>
  );
};

// Estilos minimalistas inspirados en Tidal
const main = {
  backgroundColor: '#ffffff',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
};

const container = {
  margin: '0 auto',
  padding: '40px 20px',
  maxWidth: '600px',
};

const logoSection = {
  textAlign: 'center' as const,
  marginBottom: '40px',
};

const logo = {
  margin: '0 auto',
};

const heading = {
  fontSize: '28px',
  fontWeight: '600',
  color: '#11181E',
  textAlign: 'center' as const,
  margin: '0 0 30px 0',
  lineHeight: '1.3',
};

const text = {
  fontSize: '16px',
  color: '#4B5563',
  lineHeight: '1.6',
  margin: '0 0 20px 0',
};

const orderInfoBox = {
  backgroundColor: '#FAF3F3',
  padding: '20px',
  borderRadius: '8px',
  margin: '30px 0',
};

const orderLabel = {
  fontSize: '12px',
  color: '#9CA3AF',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
  margin: '0 0 4px 0',
};

const orderValue = {
  fontSize: '16px',
  color: '#11181E',
  fontWeight: '600',
  margin: '0',
};

const productsSection = {
  margin: '30px 0',
};

const sectionTitle = {
  fontSize: '14px',
  color: '#9CA3AF',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
  margin: '0 0 16px 0',
};

const productRow = {
  marginBottom: '16px',
};

const productName = {
  fontSize: '16px',
  color: '#11181E',
  margin: '0 0 4px 0',
};

const productQuantity = {
  fontSize: '14px',
  color: '#6B7280',
  margin: '0',
};

const productPrice = {
  fontSize: '16px',
  color: '#11181E',
  fontWeight: '500',
  margin: '0',
};

const divider = {
  borderColor: '#E5E7EB',
  margin: '30px 0',
};

const totalsSection = {
  margin: '20px 0',
};

const totalRow = {
  marginBottom: '12px',
};

const totalLabel = {
  fontSize: '16px',
  color: '#6B7280',
  margin: '0',
};

const totalValue = {
  fontSize: '16px',
  color: '#11181E',
  margin: '0',
};

const totalLabelBold = {
  fontSize: '18px',
  color: '#11181E',
  fontWeight: '600',
  margin: '0',
};

const totalValueBold = {
  fontSize: '18px',
  color: '#FF3FD5',
  fontWeight: '700',
  margin: '0',
};

const shippingSection = {
  margin: '30px 0',
};

const addressText = {
  fontSize: '16px',
  color: '#4B5563',
  lineHeight: '1.6',
  margin: '0',
};

const footer = {
  fontSize: '14px',
  color: '#9CA3AF',
  textAlign: 'center' as const,
  margin: '40px 0 10px 0',
  paddingTop: '40px',
  borderTop: '1px solid #E5E7EB',
};

const footerSmall = {
  fontSize: '12px',
  color: '#D1D5DB',
  textAlign: 'center' as const,
  margin: '0',
};

OrderConfirmationEmail.PreviewProps = {
  user_name: 'Carlos',
  order_number: 'ORD-98765',
  total: 135500,
  items: [
    { name: 'Camiseta CrushMe', quantity: 2 },
    { name: 'Gorra CrushMe', quantity: 1 },
  ],
} as OrderConfirmationEmailProps;

export default OrderConfirmationEmail;
