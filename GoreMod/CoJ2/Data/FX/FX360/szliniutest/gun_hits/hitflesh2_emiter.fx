EmiterDef()
{
	Space("world")  //local  ;Model ,Instance ,Camera ,Shore, Bucket ,FX_World , FX_Camera

	GenType("one_time")  //continous ,

	GenArea("point")   //box , plane , line , radial

	LifeTime()
	{
		keyf(0.000000, 0.700000)
	}

	ParticleRate()
	{
		keyf(0, 70)
	}

	StartVelocity()
	{
		keyf(0.0, 170)
	}

	StartVelocityRand()
	{
		keyv(-0.0426745, 150, 150, 100)
	}

	Span()
	{
		keyv(0, 9, 0.399231, 0.399231)
	}

	CollisionAction("spawn_fx")  //bounce , 
    {
		Trace("CustomBulletBloodTraceGround_trace.fx")
		Probability(1.0)
	}
	
	//CollisionAction("spawn_fx")
	//{
		//ParticleEmiter("TR_hitstone_emiter.fx", "TR_hitstone_particle.fx")
	//}
	
	//AlphaFadeIn("worst", 420, 50)
	//AlphaFadeIn("best", 420, 50)
	
	//Radius()
	//{
		//keyf(0.000000, 220.000000)
	//}
	
}
