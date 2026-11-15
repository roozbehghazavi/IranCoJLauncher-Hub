EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.54)
	}

	GenType("continous")

	ParticleRate()
	{
		keyf(0, 110)
		keyf(0.112, 82.5)
		keyf(0.14, 0)
	}

	StartVelocity()
	{
		keyf(0, 110)
		keyf(0.07, 93.5)
		keyf(0.14, 66)
	}

	StartVelocityRand()
	{
		keyv(0, 4.4, 5.5, 4.4)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(0.25)
	}
}
