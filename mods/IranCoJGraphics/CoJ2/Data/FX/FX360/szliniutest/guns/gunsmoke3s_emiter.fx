EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 5)
	}

	GenType("continous")

	ParticleRate()
	{
		keyf(0, 7)
		keyf(1.8, 4)
		keyf(2.25, 0)
	}

	StartVelocity()
	{
		keyf(0, 8)
	}

	StartVelocityRand()
	{
		keyv(0, 4, 4, 4)
	}

	Direction()
	{
		keyv(0, 0, 0, 1)
	}

	GenArea("point")
}
